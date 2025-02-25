// SPDX-License-Identifier: MIT
pragma solidity >=0.8.28;

contract GameLobby {
    struct GameState {
        address[2] players;
        uint256 currentTurn;
        uint256 pot;
        uint256 currentBet;
        uint256 lastRaise;
        bool isLocked;
        bool gameStarted;
        address currentPlayer;
        BettingState bettingState;
        mapping(address => uint256) playerBets;
        mapping(address => bool) hasFolded;
    }

    struct GameConfig {
        uint256 buyInLimit;
        uint256 minBet;
        uint256 maxBet;
        uint256 maxRaises;
        address firstPlayer; // To set initial priority
    }

    enum BettingState {
        WAITING,
        BETTING_ROUND,
        RESOLVED
    }

    enum BettingActionType {
        CHECK,
        CALL,
        RAISE,
        FOLD
    }

    mapping(uint256 => GameState) public games;
    mapping(uint256 => GameConfig) public gameConfigs;
    uint256 public nextGameId;

    event GameCreated(uint256 gameId, address creator, GameConfig config);
    event PlayerJoined(uint256 gameId, address player);
    event BettingAction(uint256 gameId, address player, BettingActionType actionType, uint256 amount);
    event BettingRoundComplete(uint256 gameId);
    event PlayerFolded(uint256 gameId, address player);

    function createGame(GameConfig memory config) external payable returns (uint256) {
        require(msg.value <= config.buyInLimit, "Exceeds buy-in limit");
        require(msg.value >= config.minBet, "Below minimum buy-in");
        
        uint256 gameId = nextGameId++;
        GameState storage game = games[gameId];
        
        game.players[0] = msg.sender;
        game.currentPlayer = config.firstPlayer == address(0) ? msg.sender : config.firstPlayer;
        game.bettingState = BettingState.WAITING;
        
        gameConfigs[gameId] = config;
        
        emit GameCreated(gameId, msg.sender, config);
        return gameId;
    }

    function joinGame(uint256 gameId) external payable {
        GameState storage game = games[gameId];
        GameConfig memory config = gameConfigs[gameId];
        
        require(!game.gameStarted, "Game already started");
        require(game.players[1] == address(0), "Game full");
        require(msg.value <= config.buyInLimit, "Exceeds buy-in limit");
        require(msg.value >= config.minBet, "Below minimum buy-in");
        
        game.players[1] = msg.sender;
        game.gameStarted = true;
        game.pot = msg.value + address(this).balance;
        
        emit PlayerJoined(gameId, msg.sender);
    }

    function placeBet(uint256 gameId, BettingActionType action, uint256 amount) external payable {
        GameState storage game = games[gameId];
        GameConfig memory config = gameConfigs[gameId];
        
        require(game.gameStarted, "Game not started");
        require(game.currentPlayer == msg.sender, "Not your turn");
        require(game.bettingState != BettingState.RESOLVED, "Betting round resolved");
        require(!game.hasFolded[msg.sender], "Player folded");

        if (action == BettingActionType.FOLD) {
            game.hasFolded[msg.sender] = true;
            _resolveBettingRound(gameId);
            emit PlayerFolded(gameId, msg.sender);
            return;
        }

        if (action == BettingActionType.CHECK) {
            require(game.currentBet == game.playerBets[msg.sender], "Cannot check");
        } else if (action == BettingActionType.CALL) {
            uint256 callAmount = game.currentBet - game.playerBets[msg.sender];
            require(msg.value == callAmount, "Incorrect call amount");
            game.playerBets[msg.sender] += callAmount;
            game.pot += callAmount;
        } else if (action == BettingActionType.RAISE) {
            require(amount <= config.maxBet, "Exceeds max bet");
            require(amount >= config.minBet, "Below min bet");
            require(amount > game.currentBet, "Raise must be higher than current bet");
            
            uint256 raiseAmount = amount - game.playerBets[msg.sender];
            require(msg.value == raiseAmount, "Incorrect raise amount");
            
            game.currentBet = amount;
            game.playerBets[msg.sender] += raiseAmount;
            game.pot += raiseAmount;
            game.lastRaise = amount;
        }

        _updateTurn(gameId);
        emit BettingAction(gameId, msg.sender, action, amount);
    }

    function _updateTurn(uint256 gameId) private {
        GameState storage game = games[gameId];
        
        // Switch to the other player
        game.currentPlayer = game.currentPlayer == game.players[0] ? game.players[1] : game.players[0];
        
        // Check if betting round is complete
        if (game.playerBets[game.players[0]] == game.playerBets[game.players[1]]) {
            _resolveBettingRound(gameId);
        }
    }

    function _resolveBettingRound(uint256 gameId) private {
        GameState storage game = games[gameId];
        game.bettingState = BettingState.RESOLVED;
        game.isLocked = false;
        
        // Reset betting state for next round
        game.currentBet = 0;
        game.lastRaise = 0;
        game.playerBets[game.players[0]] = 0;
        game.playerBets[game.players[1]] = 0;
        
        emit BettingRoundComplete(gameId);
    }

    function startNewBettingRound(uint256 gameId) external {
        GameState storage game = games[gameId];
        require(game.bettingState == BettingState.RESOLVED, "Previous round not resolved");
        require(!game.isLocked, "Game is locked");
        
        game.bettingState = BettingState.BETTING_ROUND;
        game.isLocked = true;
    }

    function getGameState(uint256 gameId) external view returns (
        address[2] memory players,
        uint256 pot,
        uint256 currentBet,
        address currentPlayer,
        BettingState bettingState,
        bool isLocked
    ) {
        GameState storage game = games[gameId];
        return (
            game.players,
            game.pot,
            game.currentBet,
            game.currentPlayer,
            game.bettingState,
            game.isLocked
        );
    }
}
