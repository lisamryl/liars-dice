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
    for (let player_id in request) {
    $('#die-roll-' + player_id).empty();

    $('#die-roll-' + player_id).append(`Die Roll: [${request['player_id']}]`);
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
    $.post('/finishturn.json', {'game_id': game_id}, rollDice);
    setTimeout(function () { window.location.reload(); }, 1000);
    $('.start-new-turn').hide();
    // }
}

function askToStartRound(request) {
    console.log("got asked to start round...");
    $('.start-new-turn').show();
    $('.start-bid').hide();
    $('#bid-form').hide();
    if (request['bid'] == 'game_over') {
        window.location.replace(`/game_over/${request['game_id']}`);
    }
    else {
        setTimeout(function () { window.location.reload(); }, 1000);
        console.log("showing next turn");
        $('.start-new-turn').show();
        $('.start-bid').hide();
        $('#bid-form').hide();
    }
}


function challengeOrExact(request) {
//handle case where challenge is called
    console.log("challenge or exact function called");
    let formInputs = {'game_id': request['game_id'], 'bid': request['bid']};
    $.post('/endturn.json', formInputs, askToStartRound);
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
        $('#bids').append(
            `<tr>
            <td class='player-name'>${request['name']}</td>
            <td class='die-choice'>${request['die_choice']}</td>
            <td class='die-count'>${request['die_count']}</td>
            </tr>`);
        console.log("updating bids");
        $('#turn-marker').empty();
        $('#turn-marker').append(`Current Turn: ${request['turn_marker_name']}`);

        if (request['turn_marker'] == 1) {
            $('#player-bidding-div').show();
            $('.start-bid').hide();
        }
        else {
            $('#player-bidding-div').hide();
            setInterval(compTurn(request['game_id']), 500);
        }
    }
}

$('.start-new-turn').on('click', startRound)

$('.start-bid').on('click', function () {
        let game_id = getGameId(window.location);
        setInterval(compTurn(game_id), 500); 
});

// $( document ).ready(function () {
//     console.log("reached load function");
//     if (request[current_turn_marker] == 1) {
//         $('#player-bidding-div').show();
//     }
//     else {
//         let game_id = getGameId(window.location);
//         setInterval(compTurn(game_id), 500);         
//     }
// });
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

$('.bid-type').on('click', function (evt) {
    let bid = evt.target.value;
    let game_id = getGameId(window.location);
    console.log(game_id);
    $.post('/endturn.json', {'game_id': game_id, 'bid': bid}, askToStartRound);

});
