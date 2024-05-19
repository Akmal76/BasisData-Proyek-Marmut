-- Membuat trigger tambah_total_play yang dijalankan sebelum insert pada tabel playlist_song
CREATE OR REPLACE FUNCTION perbarui_total_play() RETURNS TRIGGER AS
$$
    DECLARE
        jumlah_play INTEGER;
    BEGIN
        -- Ambil nilai total_play dari tabel song untuk id_konten yang sama dengan id_song baru
        SELECT total_play INTO jumlah_play 
        FROM song 
        WHERE id_konten = NEW.id_song;
        
        -- Tambahkan 1 ke nilai jumlah_play
        jumlah_play := jumlah_play + 1;
        
        -- Perbarui nilai total_play di tabel song dengan nilai jumlah_play yang baru
        UPDATE song 
        SET total_play = jumlah_play 
        WHERE id_konten = NEW.id_song;
        
        RETURN NEW;
    END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tambah_total_play
BEFORE INSERT ON playlist_song
FOR EACH ROW
EXECUTE FUNCTION perbarui_total_play();

-- Membuat trigger tambah_total_download yang dijalankan sebelum insert pada tabel downloaded_song
CREATE OR REPLACE FUNCTION perbarui_total_download() RETURNS TRIGGER AS
$$
    DECLARE
        jumlah_download INTEGER;
    BEGIN
        -- Ambil nilai total_download dari tabel song untuk id_konten yang sama dengan id_song baru
        SELECT total_download INTO jumlah_download 
        FROM song 
        WHERE id_konten = NEW.id_song;
        
        -- Tambahkan 1 ke nilai jumlah_download
        jumlah_download := jumlah_download + 1;
        
        -- Perbarui nilai total_download di tabel song dengan nilai jumlah_download yang baru
        UPDATE song 
        SET total_download = jumlah_download 
        WHERE id_konten = NEW.id_song;
        
        RETURN NEW;
    END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tambah_total_download
BEFORE INSERT ON downloaded_song
FOR EACH ROW
EXECUTE FUNCTION perbarui_total_download();
