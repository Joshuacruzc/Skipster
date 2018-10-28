$(function() {
    $('#search_button').click(function() {
        var query = $('#search_bar').val();
        $.ajax({
            url: '/search_tracks',
            data: {'query': query},
            type: 'POST',
            success: function(response) {
                var track_list = $("#track_list");
                track_list.empty();
                for(var i=0; i<response.length; i++) {
                    track_list.append("<li>" + response[i]['name'] + " by " + response[i]['artist'] + "</li>");
                    var item = $('#track_list li').last();
                    item.attr('data-uri', response[i]['uri']);
                    item.attr('data-name', response[i]['name']);
                    item.attr('data-artist', response[i]['artist']);
                    item.attr('data-album', response[i]['album']);
                    item.attr('data-artwork', response[i]['artwork']);
                    item.prepend("<img src=" + response[i]['artwork'] + ">");
                    item.append("<button class='vote'>Vote!</button>");
                }
                $('.vote').click(function () {
                    var track = $(this).parent();
                    var playlist = $('#playlist');
                    $.ajax({
                        url: '/vote',
                        data: {
                            'playlist_id': playlist.attr('data-id'),
                            'playlist_uri': playlist.attr('data-uri'),
                            'uri': track.attr('data-uri'),
                            'name': track.attr('data-name'),
                            'artist': track.attr('data-artist'),
                            'album': track.attr('data-album'),
                            'artwork': track.attr('data-artwork')
                        },
                        type: 'POST',
                        success: function (response) {
                            track.html(response);
                        },
                        error: function (error) {
                            console.log(error);
                            track.append('an error occurred while processing this request');
                        }
                    });
                });
            },
            error: function(error) {
                console.log(error);
                $('#track_list').html(error);
            }
        });
    });
});