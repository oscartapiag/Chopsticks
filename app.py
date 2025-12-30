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
    
    game = get_game(session_id)
    
    return {
        "human_hands": [game.left(0), game.right(0)],
        "ai_hands": [game.left(1), game.right(1)],
        "turn": "human" if game.turn == 0 else "ai",
        "winner": game.winner()
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
             return {"status": "game_over", "winner": "human" if winner == 0 else "ai"}
             
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
         pass
         
    if game.winner() is not None:
        return {"status": "game_over", "winner": "human" if game.winner() == 0 else "ai"}

    try:
        # AI finds move
        move = game.ai_move()
        # AI makes move
        game.apply_move(move)
        game.next_turn()
        
        return {
            "ai_move_made": move,
            "winner": game.winner()
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
        # Keep same difficulty? We need to store it or default to 5
        # For simple reset, lets stick to default 5 or reuse existing attr if we had it
        # Actually, let's just make reset restart the CURRENT game logic
        # But Game class init resets state. 
        # We should probably store depth in Game instance? 
        # stick.py Player doesn't store depth. AI.py does.
        # AI(difficulty) sets self.DEPTH
        # Let's peek at existing game's AI depth
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
