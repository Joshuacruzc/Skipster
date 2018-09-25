$('.remove').click(function() {
                    var track = $(this).parent();
                    var playlist = $('#playlist');
                    $.ajax({
                        url: '/remove_track',
                        data: {
                            'playlist_id': playlist.attr('data-id'),
                            'playlist_uri': playlist.attr('data-uri'),
                            'uri': track.attr('data-uri'),
                        },
                        type: 'POST',
                        success: function(response) {
                            track.html(response);
                        },
                        error: function(error) {
                            console.log(error);
                            track.append('an error occurred while processing this request');
                        }
                    });
                });