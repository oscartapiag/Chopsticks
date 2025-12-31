from fastapi import FastAPI, HTTPException, Request, Response, Body, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import os

# Import existing game logic
from game import Game

app = FastAPI()

# -----------------------------------------------------------------------------
# State Management
# -----------------------------------------------------------------------------
# In a real production app, use Redis or a database. 
# For this "game on a website", in-memory is fine, but we must handle concurrency.
games: Dict[str, Game] = {}

def get_game(session_id: str) -> Game:
    if session_id not in games:
        # Create a new game for this session
        games[session_id] = Game(vs_ai=True)
    return games[session_id]

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class MoveRequest(BaseModel):
    m0: str  # 'l', 'r', 's'
    m1: str  # 'l', 'r'

# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------

@app.get("/api/state")
def get_state(request: Request, response: Response, session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id)
    
        response.set_cookie(key="session_id", value=session_id)
    
    # Disable Caching
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    game = get_game(session_id)
    
    winner = game.winner()
    w_str = None
    if winner is not None:
        if winner == 0: w_str = "human"
        elif winner == 1: w_str = "ai"
        elif winner == 2: w_str = "human_stalemate"
        elif winner == 3: w_str = "ai_stalemate"
        else: w_str = "draw"

    return {
        "human_hands": [game.left(0), game.right(0)],
        "ai_hands": [game.left(1), game.right(1)],
        "turn": "human" if game.turn == 0 else "ai",
        "winner": w_str,
        "difficulty": game.ai.DEPTH if hasattr(game.ai, 'DEPTH') else 5
    }

@app.post("/api/move")
def make_move(move: MoveRequest, request: Request, session_id: Optional[str] = Cookie(None)):
    if not session_id or session_id not in games:
        raise HTTPException(status_code=400, detail="No active game session")
    
    game = games[session_id]
    
    if game.turn != 0:
        raise HTTPException(status_code=400, detail="It is not your turn")
    
    # Construct move tuple for the existing python logic
    # The logic expects a tuple usually, let's check stick.py make_move signature
    # stick.py expects Target+Source notation for attacks (e.g. 'rl' = Target Right, Source Left)
    # But expects 's'+Source for splits.
    
    if move.m0 == 's':
        move_seq = move.m0 + move.m1
    else:
        # Swap for attack: m1 (Target) + m0 (Source)
        move_seq = move.m1 + move.m0
    
    try:
        game.apply_move(move_seq)
        game.next_turn()
        
        # Check winner immediately
        winner = game.winner()
        if winner is not None:
             # 0: Human, 1: AI, 2: Human (Stalemate), 3: AI (Stalemate), -1: Tie
             if winner == 0: w_str = "human"
             elif winner == 1: w_str = "ai"
             elif winner == 2: w_str = "human_stalemate"
             elif winner == 3: w_str = "ai_stalemate"
             else: w_str = "draw"
             
             return {"status": "game_over", "winner": w_str}
             
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok", "turn": "ai"}

@app.post("/api/ai_move")
def trigger_ai(request: Request, session_id: Optional[str] = Cookie(None)):
    if not session_id or session_id not in games:
        raise HTTPException(status_code=400, detail="No active game session")
    
    game = games[session_id]
    
    if game.turn != 1:
         # It might still be human turn if they clicked fast? 
         # Or maybe the frontend is polling.
         raise HTTPException(status_code=400, detail="Not AI turn")
         
    if game.winner() is not None:
        winner = game.winner()
        if winner == 0: w_str = "human"
        elif winner == 1: w_str = "ai"
        elif winner == 2: w_str = "human_stalemate"
        elif winner == 3: w_str = "ai_stalemate"
        else: w_str = "draw"
        return {"status": "game_over", "winner": w_str}

    try:
        move = game.ai_move()
        # AI makes move
        game.apply_move(move)
        game.next_turn()
        
        # Helper to map winner
        winnerCode = game.winner()
        if winnerCode == 0: ws = "human"
        elif winnerCode == 1: ws = "ai"
        elif winnerCode == 2: ws = "human_stalemate"
        elif winnerCode == 3: ws = "ai_stalemate"
        else: ws = "draw"
        
        return {
            "ai_move_made": move,
            "winner": ws if winnerCode is not None else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GameConfig(BaseModel):
    depth: int

@app.post("/api/new_game")
def new_game(config: GameConfig, response: Response, session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id)
    
    games[session_id] = Game(vs_ai=True, depth=config.depth)
    return {"status": "created"}

@app.post("/api/reset")
def reset_game(response: Response, session_id: Optional[str] = Cookie(None)):
    if session_id and session_id in games:
        old_game = games[session_id]
        depth = old_game.ai.DEPTH if hasattr(old_game.ai, 'DEPTH') else 5
        games[session_id] = Game(vs_ai=True, depth=depth)
    return {"status": "reset"}

# -----------------------------------------------------------------------------
# Static Files & Views
# -----------------------------------------------------------------------------

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_home():
    return FileResponse('templates/home.html')

@app.get("/game")
async def read_game():
    return FileResponse('templates/index.html')
