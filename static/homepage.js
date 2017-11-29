"use strict";

//Javascript on homepage
function showSavedGames(results) {
    let game_ids = results['games'];
    if (results['games']) {
        $('#loaded-games').empty();
        $('#loaded-games').append(`<p><ul>`);
        for (let i in results['games']) {
            $('#loaded-games').append(`<a href='/game/${game_ids[i]}'>Game ${game_ids[i]}</a><br>`);
        }
        $('#loaded-games').append(`</ul></p>`);
    }
    else {
        $('#loaded-games').append(`<p>You have no saved games, create a new one!</p>`);
    }
}


$('#load-inprogress-games').on('click', function (evt) {
    console.log("pressed load games");
    evt.preventDefault();
    $.get('/loadgames.json', showSavedGames);
});
