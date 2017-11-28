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

    let game_id = getGameId(window.location);
    //restarting round, clear out game messages, clear out probability table,
    //and clear out bidding table.
    $('#game-messages').empty();
    $('#bids').empty();
    $('#probs').empty();
    //Post to roll dice
    $.post('/finishturn.json', {'game_id': game_id}, rollDice);
     //Show only needed information
    $.get('/game_details.json', {'game_id': game_id}, hideAndUnhide);
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
        let game_id = getGameId(window.location);
        $.get('/game_details.json', {'game_id': game_id, 'starting_turn': true}, hideAndUnhide);
    }
}


function challengeOrExact(request) {
//handle case where challenge is called by computer
    console.log("challenge or exact function called");
    let formInputs = {'game_id': request['game_id'], 'bid': request['bid']};
    $.post('/endturn.json', formInputs, askToStartRound);
}

function updateOptions(response) {
    //Update options to choose from in form based on current bid
    console.log("update options called");
    $("#player-die-count-choices").empty();
    $("#player-die-count-choices").append(`<select name = 'player-die-count'>`)
    // default values if first bid
    let dieCount = 0;
    let dieChoice = 6;
    if (response['die_count']) {
        // if there's a previous bid, set it
        console.log("entered if");
        dieCount = parseInt(response['die_count']);
        dieChoice = parseInt(response['die_choice']);
    }
    let playerDieChoice = parseInt($("#player-die-choice").val());
    let totalDice = parseInt(response['total_dice']);

    console.log(dieCount);
    console.log(response['die_choice']);
    console.log(response['total_dice']);
    let dropdown = $("<select>");
    dropdown.attr("name", "player-die-count");
    console.log($("#player-die-choice").val());

    for (let i = 0; i <= totalDice; i += 1) {
        if (i > dieCount && playerDieChoice <= dieChoice ||
           i >= dieCount && playerDieChoice > dieChoice)  {
           let option = $("<option>");
           option.attr("value", i);
           option.append(i + " dice");
           dropdown.append(option);
        }
    }
    $("#player-die-count-choices").empty();
    $("#player-die-count-choices").append(dropdown);
}


function hideAndUnhide(response) {
    console.log("hide and unhide called");
    console.log(response);
    if (response["starting_turn"] == false) {
        console.log("hide start new turn");
        $('.start-new-turn').hide();
            if (response["turn_marker"] == 1) {
                console.log("show player details");
                $('#player-bidding-tables').show();
                $('#bid-probs').show();
                $('.start-bid').hide();
                // update options for case where user doesn't change die choice
                updateOptions(response);
                updateProbs(response);
                if (!response["die_choice"]) {
                    // check if this is the first bid, if so, don't allow challenge/exact
                    $('#challenge-exact').hide()
                }
            }
            else {
                console.log("show comp buttons");
                $('#player-bidding-tables').hide();
                $('#bid-probs').hide();
                $('.start-bid').show();
            }
    }
    else {
        console.log("show start new turn");
        $('.start-new-turn').show();
        $('#player-bidding-tables').hide();
        $('#bid-probs').hide();       
        $('.start-bid').hide();
    }
}


function updateProbs(request) {
    //Update bidding probabilities for a player
    console.log("update probs called");
    $('#bid-probs').show();
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
        $('#turn-marker').empty();
        console.log(request['turn_marker_name']);
        console.log(request['turn_marker']);
        $('#turn-marker').append(`Current Turn: ${request['turn_marker_name']}`);

        if (request['turn_marker'] == 1) {
            console.log("showing player bidding");
            $('#player-bidding-tables').show();
            $('.start-bid').hide();
            //Update bidding probabilities table
            updateProbs(request);
            updateOptions(request);
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
    console.log("player chose challenge/exact");
    let bid = evt.target.value;
    let game_id = getGameId(window.location);
    console.log(game_id);
    $.post('/endturn.json', {'game_id': game_id, 'bid': bid}, askToStartRound);

});

//update options for die count when die choice is changed
$('#player-die-choice').on('change', function (evt) {
    let game_id = getGameId(window.location);
    $.get('/game_details.json', {'game_id': game_id}, updateOptions);
});

//hover over tips
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
});

//hide and show items
$(document).ready(function(){
    console.log("showing and hidding");
    let game_id = getGameId(window.location);
    $.get('/game_details.json', {'game_id': game_id}, hideAndUnhide);
});

