/*
Memperbarui durasi saat Menambahkan atau Menghapus Episode dalam Podcast:
Ketika Podcaster menambahkan atau menghapus episode dalam suatu podcast,
sistem dapat memperbarui atribut durasi dari podcast tersebut dalam tabel KONTEN.
*/

CREATE OR REPLACE FUNCTION update_podcast_duration_on_delete()
RETURNS TRIGGER AS
$$
BEGIN
    UPDATE konten
    SET durasi = durasi - OLD.durasi
    WHERE id = OLD.id_konten_podcast;
    
    RETURN OLD;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER update_podcast_duration_trigger_delete
AFTER DELETE ON episode
FOR EACH ROW
EXECUTE FUNCTION update_podcast_duration_on_delete();

/*
Memperbarui Atribut Durasi dan Jumlah Lagu:
Ketika lagu ditambahkan atau dihapus dari album,
diperlukan pembaruan atribut total_durasi dan jumlah_lagu dari tabel ALBUM..
*/

CREATE OR REPLACE FUNCTION UpdateAlbumStats(album_id_param uuid) 
RETURNS void AS $$
DECLARE
    total_duration INT;
    total_songs INT;
BEGIN
    -- Menghitung total durasi lagu dan jumlah lagu dari album
    SELECT SUM(konten.durasi), COUNT(*)
    INTO total_duration, total_songs
    FROM song
    JOIN konten ON song.id_konten = konten.id
    WHERE song.id_album = album_id_param;

    -- Memperbarui atribut total_durasi dan jumlah_lagu pada tabel ALBUM
    UPDATE album
    SET total_durasi = total_duration, jumlah_lagu = total_songs
    WHERE id = album_id_param;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION UpdateAlbumStatsTrigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Memanggil stored procedure UpdateAlbumStats saat lagu ditambahkan atau dihapus dari album
    IF TG_OP = 'INSERT' THEN
        PERFORM UpdateAlbumStats(NEW.id_album);
    ELSEIF TG_OP = 'DELETE' THEN
        PERFORM UpdateAlbumStats(OLD.id_album);
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER UpdateAlbumStatsTriggerAfterInsert
AFTER INSERT ON song
FOR EACH ROW
EXECUTE FUNCTION UpdateAlbumStatsTrigger();

CREATE TRIGGER UpdateAlbumStatsTriggerAfterDelete
AFTER DELETE ON song
FOR EACH ROW
EXECUTE FUNCTION UpdateAlbumStatsTrigger();