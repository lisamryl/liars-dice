"use strict";

function get_game_id(url) {
    // Returns game id of active game, based on url passed in
    // below syntax from Stack O. to pull last piece of url out as the game_id
    return url.href.substring(url.href.lastIndexOf('/') + 1); 
}

function rollDice(request) {

    //Refresh data in player details
    for (let player_id in request) {
    $('#die-roll-' + player_id).empty();

    $('#die-roll-' + player_id).append(
        `Die Roll: [${request[player_id]}]`
        );

    }

}


function showBid(request) {


}

$('.roll-dice').on('click', function () {

    let game_id = get_game_id(window.location);
    $.post('/rolldice', {'game_id': game_id}, rollDice);

});

$('.start-bid').on('click', function () {
    let game_id = get_game_id(window.location);
    $.post('/startbid', {'game_id': game_id}, showBid);

}

