// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.28 <0.9.0;

import { Test } from "forge-std/src/Test.sol";
import { console2 } from "forge-std/src/console2.sol";

import { GameLobby } from "../src/GameLobby.sol";

contract GameLobbyTest is Test {
    GameLobby internal gameLobby;

    function setUp() public {
        gameLobby = new GameLobby();
    }
}