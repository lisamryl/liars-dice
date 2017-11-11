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

    $('#die-roll-' + player_id).append(`Die Roll: [${request[player_id]}]`);
    }
}


function challenge(request) {
//handle case where challenge is called
    $.post('/endturn.json', {'game_id': game_id}, startRound);
}

function exact(request) {
//handle case where exact is called

}


function handleBid(request) {
//handle the bid provided by the player or computer
if (request['die_choice'] == "Challenge") {
    challenge(request);
}
else if (request['die_choice'] == "Exact") {
    exact(request);
}

else {
    $('#bids').append(
        `<tr>
        <td class='player-name'>${request['name']}</td>
        <td class='die-choice'>${request['die_choice']}</td>
        <td class='die-count'>${request['die_count']}</td>
        </tr>`);
    $('#turn-marker').empty();
    $('#turn-marker').append(`Current Turn: ${request['turn_marker_name']}`);

    if (request['turn_marker'] == 1) {
        $('#player-bidding-div').show();
        }
    else {
        $('#player-bidding-div').hide();  
        }
    }
}

$('.roll-dice').on('click', function () {

    let game_id = get_game_id(window.location);
    $.post('/rolldice.json', {'game_id': game_id}, rollDice);

});

$('.start-bid').on('click', function () {
    let game_id = get_game_id(window.location);
    $.post('/compturn.json', {'game_id': game_id}, handleBid);
});

// player turn - after submitting
$('#bid-form').on('submit', function (evt) {
    evt.preventDefault()
    let formInputs = {
    "die_choice": $("[name='player-die-choice']").val(),
    "die_count": $("[name='player-die-count']").val(),
    "game_id": $("[name='game-id']").val()
};
    $.post('/playerturn.json', formInputs, handleBid);
});