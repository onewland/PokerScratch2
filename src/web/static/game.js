"use strict";

let setActionsEnabled = (player, game) => {
    $(".on-turn-only-action").prop('disabled', player.id !== game.betting_round.current_bettor.id);
};

$(() => {
    $.getJSON('/v1/game', (data) =>
        setActionsEnabled(data.player, data.game)
    )
});