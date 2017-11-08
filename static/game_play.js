"use strict";

function rollDice(request) {

    window.location.reload();

    // Refresh data in player details - need to work on optimizing this code.
    // $('#player-details').empty();

    // $('#player-details').append(
    //     `<ul class = 'player-details'>
    //     {% for player in players %}
    //         <li>Name: {{ player.name }}; Die Count: {{ player.die_count }};
    //             Position: {{ player.position }}
    //             Die Roll: {{ player.current_die_roll }}
    //             {% if player.comp %}
    //             Liar: {{ player.comp.liar_factor }}
    //             Aggr: {{ player.comp.aggressive_factor }}
    //             Intel: {{ player.comp.intelligence_factor }}
    //             {% endif %}
    //         </li>
    //     {% endfor %}
    //     </ul>`
    //     )
}



$('.roll-dice').on('click', function () {
    let url = window.location;
    // below syntax from Stack O. to pull last piece of url out as the game_id
    let game_id = url.href.substring(url.href.lastIndexOf('/') + 1); 
    $.post('/rolldice', {'game_id': game_id}, rollDice);

});


