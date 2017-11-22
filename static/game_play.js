"use strict";

//Javascript on homepage
function showSavedGames(results) {
    let game_ids = results['games'];
    if (results['games']) {
        $('#loaded-games').append(`<p><ul>`);
        for (let i in results['games']) {
            $('#loaded-games').append(`<a href='/game/${game_ids[i]}'>Game ${game_ids[i]} - Click to Resume Play</a><br>`);
        }
        $('#loaded-games').append(`</ul></p>`);
    }
    else {
        $('#loaded-games').append(`<p>You have no saved games, create a new one!</p>`);
    }
}


$('#load-game').on('click', function (evt) {
    console.log("pressed load games");
    evt.preventDefault();
    $.get('/loadgames.json', showSavedGames);
});


//Javascript on Game page
function getGameId(url) {
    // Returns game id of active game, based on url passed in
    // below syntax from Stack O. to pull last piece of url out as the game_id
    return url.href.substring(url.href.lastIndexOf('/') + 1); 
}

function rollDice(request) {

    //Refresh data in player details
    console.log("dice rolled");
    console.log(request);
    for (let player_id in request) {
        $('#die-count-' + player_id).empty();
        $('#die-count-' + player_id).append(`Die Count: ${request[player_id].length}`);
        $('#die-roll-' + player_id).empty();
        $('#die-roll-' + player_id).append(`Die Roll: [${request[player_id]}]`);
    }
}


function compTurn(game_id) {
    $.post('/compturn.json', {'game_id': game_id}, handleBid);
}


function startRound(request) {
//restart round (roll dice and begin bidding)
    console.log("start round was called");
    console.log(request);

    let game_id = getGameId(window.location);
    //restarting round, clear out game messages, clear out probability table,
    //and clear out bidding table.
    $('#game-messages').empty();
    $('#bids').empty();
    $('#probs').empty();
    //Hide "start new turn", we don't need it anymore
    $('.start-new-turn').hide();

    if (request['turn_marker'] == 1) {
        //if human's turn, show their bid form, hid option to start opponent bids
        $('#player-bidding-tables').show();
        $('.start-bid').hide();
    }
    else {
        //if AI turn, hide human bid form, show button to start opponent bids.
        $('#player-bidding-tables').hide();
        $('.start-bid').show();
    }
    $.post('/finishturn.json', {'game_id': game_id}, rollDice);
}

function askToStartRound(request) {
    console.log("got asked to start round...");
    // if game over, bring to game over screen
    if (request['bid'] == 'game_over') {
        window.location.replace(`/game_over/${request['game_id']}`);
    }
    else {
        // add messages about what happened in the last round
        $('#game-messages').empty();
        console.log(request['messages']);
        $('#game-messages').append(`<ul>`);
        for (let i = 0; i < (request['messages'].length); i += 1) {
            $('#game-messages').append(`<li>${request['messages'][i]}</li>`);            
        }
        $('#game-messages').append(`</ul>`);
        // show button for player to start the next turn (hide all other buttons)
        console.log("showing next turn");
        $('.start-new-turn').show();
        $('.start-bid').hide();
        $('#player-bidding-tables').hide();
    }
}


function challengeOrExact(request) {
//handle case where challenge is called by computer
    console.log("challenge or exact function called");
    let formInputs = {'game_id': request['game_id'], 'bid': request['bid']};
    $.post('/endturn.json', formInputs, askToStartRound);
}

function updateOptions(request) {
    //Update options to choose from in form based on current bid
    console.log("update options called");
    $("#player-die-count-choices").empty();
    $("#player-die-count-choices").append(`<select name = 'player-die-count'>`)
    for (let i = 0; i <= request['total_dice']; i += 1) {
        if (i > request['die_count'] && $("#player-die-choice").val() <= request['die_choice']) {
           $("#player-die-count-choices").append(`<option value="${i}">${i} dice</option>`);
           console.log(i);
        }
    }
    $("#player-die-count-choices").append(`</select>`)
}


function handleBid(request) {
//handle the bid provided by the player or computer
    console.log("handle bid called");
    console.log("start new turn hidden");
    $('.start-new-turn').hide();
    if (request['bid'] == 'challenge' | request['bid'] == 'exact') {
        console.log("reached if statement true");
        challengeOrExact(request);
    }

    else {
        console.log("got to editing bids");
        $('#bids').append(
            `<tr>
            <td class='player-name'>${request['name']}</td>
            <td class='die-choice'>${request['die_choice']}</td>
            <td class='die-count'>${request['die_count']}</td>
            </tr>`);
        console.log("updating bids");
        $('#turn-marker').empty();
        console.log(request['turn_marker_name']);
        console.log(request['turn_marker']);
        $('#turn-marker').append(`Current Turn: ${request['turn_marker_name']}`);

        if (request['turn_marker'] == 1) {
            $('#player-bidding-tables').show();
            $('.start-bid').hide();
            //Update bidding probabilities table
            $('#probs').empty();
            for (let die_choice in request['player_probs']) {
                for (let die_count in request['player_probs'][die_choice]) {
                    $('#probs').append(`<tr>
                        <td>${die_choice}</td>
                        <td>${die_count}</td>
                        <td>${Math.round(request['player_probs'][die_choice][die_count] * 100)}%</td>
                        </tr>`);
                }
            }
            updateOptions(request)
        }
        else {
            console.log("hidding player bidding div for comp turn");
            $('#player-bidding-tables').hide();
            setInterval(compTurn(request['game_id']), 500);
        }
    }
}

$('.start-new-turn').on('click', startRound)

$('.start-bid').on('click', function () {
        let game_id = getGameId(window.location);
        setInterval(compTurn(game_id), 500); 
});

//when player submits a bid
$('#bid-form').on('submit', function (evt) {
    evt.preventDefault()
    let formInputs = {
    "die_choice": $("[name='player-die-choice']").val(),
    "die_count": $("[name='player-die-count']").val(),
    "game_id": $("[name='game-id']").val()
    };
    $.post('/playerturn.json', formInputs, handleBid);
});

//clicked when player chooses challenge or exact
$('.bid-type').on('click', function (evt) {
    let bid = evt.target.value;
    let game_id = getGameId(window.location);
    console.log(game_id);
    $.post('/endturn.json', {'game_id': game_id, 'bid': bid}, askToStartRound);

});

//update options for die count when die choice is changed
$('#player-die-choice').on('change', updateOptions)

//hover over tips
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
});
