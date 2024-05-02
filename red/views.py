from django.shortcuts import render

from django.http import HttpResponse

def show_create_album(request):
    if request.method == 'POST':
        judul = request.POST.get('judul')
        label = request.POST.get('label')
        
        return HttpResponse("Album created successfully.")
    
    else:
        # Dummy
        labels = ['Label 1', 'Label 2', 'Label 3']
        
        return render(request, 'create_album.html', {'labels': labels})


def show_create_lagu(request):
    if request.method == 'POST':
        album = request.POST.get('album')
        judul = request.POST.get('judul')
        artist = request.POST.get('artist')
        songwriter = request.POST.getlist('songwriter')  # For multi-select
        genre = request.POST.getlist('genre')  # For multi-select
        durasi = request.POST.get('durasi')
        
        return HttpResponse("Song created successfully.")
    
    else:
        #Dummy
        artists = ['Artist 1', 'Artist 2', 'Artist 3']
        songwriters = ['Songwriter 1', 'Songwriter 2', 'Songwriter 3']
        genres = ['Genre 1', 'Genre 2', 'Genre 3']
        
        user_role = 'Artist'
        user_name = 'John Doe'

        selected_album = 'Album1'
        
        return render(request, 'create_lagu.html', {'artists': artists, 'songwriters': songwriters, 'genres': genres, 'user_role': user_role, 'user_name': user_name, 'selected_album': selected_album})

def list_album(request):
    # Dummy
    albums = [
        {'judul': 'Album1', 'label': 'LabelA', 'jumlah_lagu': 0, 'total_durasi': '0 menit'},
        {'judul': 'Album2', 'label': 'LabelB', 'jumlah_lagu': 2, 'total_durasi': '4 menit'},
        # Add more albums as needed
    ]

    user_role = 'artist' 

    return render(request, 'list_album.html', {'albums': albums, 'user_role': user_role})

def list_song(request):
    #Dummy
    album_title = "Album1"
    songs = [
        {'judul': 'Lagu1', 'durasi': '2 menit', 'total_play': 3, 'total_download': 0},
        {'judul': 'Lagu2', 'durasi': '3 menit', 'total_play': 2, 'total_download': 2},
    ]

    return render(request, 'list_song.html', {'album_title': album_title, 'songs': songs})

def list_royalti(request):
    royalties = [
        {'judul_lagu': 'Lagu1', 'judul_album': 'Album1', 'total_play': 3, 'total_download': 0, 'total_royalti': 'Rp 450000'},
        {'judul_lagu': 'Lagu2', 'judul_album': 'Album2', 'total_play': 2, 'total_download': 2, 'total_royalti': 'Rp 520000'},

    ]
    return render(request, 'list_royalti.html', {'royalties': royalties})
