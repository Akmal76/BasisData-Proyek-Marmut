/* 
Pengecekan Email:
Ketika ada akun baru yang mendaftar (baik role Pengguna maupun Label),
sistem terlebih dahulu mengecek apakah email sudah terdaftar atau belum. 
Jika email sudah terdaftar, keluarkan pesan error.
*/

CREATE OR REPLACE FUNCTION check_existing_email()
RETURNS TRIGGER AS
$$
BEGIN
    -- Periksa apakah email yang baru mendaftar sudah terdaftar sebelumnya dalam tabel akun
    IF EXISTS (SELECT 1 FROM akun WHERE email = NEW.email) THEN
        -- Jika email sudah terdaftar, kirimkan pesan error
        RAISE EXCEPTION 'Email % sudah terdaftar.', NEW.email;
    END IF;
    
    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER check_existing_email_trigger
BEFORE INSERT ON akun
FOR EACH ROW
EXECUTE FUNCTION check_existing_email();

/*
Pendaftaran Pengguna Baru:
Ketika Pengguna baru yang mendaftar, sistem secara otomatis menetapkan pengguna memiliki akun non-premium.
*/

CREATE OR REPLACE FUNCTION set_nonpremium_on_registration()
RETURNS TRIGGER AS
$$
BEGIN
    -- Set is_verified menjadi false dan menetapkan pengguna sebagai non-premium saat pendaftaran
    NEW.is_verified := false;

    RETURN NEW;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER set_nonpremium_trigger
BEFORE INSERT ON akun
FOR EACH ROW
EXECUTE FUNCTION set_nonpremium_on_registration();

/*
Memeriksa status langganan Pengguna:
(Stored procedure yang dapat dijalankan di backend)
Ketika Pengguna melakukan login, melakukan pemeriksaan status langganan. Apabila status langganan Premium,
jika timestamp_berakhir lebih dari tanggal hari ini ubah status langganan menjadi Non Premium. 
*/

CREATE OR REPLACE PROCEDURE login_and_update_subscription(email_param CHARACTER VARYING) AS $$
DECLARE
    l_is_verified BOOLEAN;
    l_timestamp_berakhir TIMESTAMP;
BEGIN
    -- Ambil status langganan pengguna yang melakukan login dari tabel transaction
    SELECT a.is_verified, t.timestamp_berakhir
    INTO l_is_verified, l_timestamp_berakhir
    FROM akun a
    JOIN transaction t ON a.email = t.email
    WHERE a.email = email_param
    ORDER BY t.timestamp_berakhir DESC
    LIMIT 1;

    -- Periksa apakah pengguna memiliki langganan premium dan apakah langganan telah berakhir
    IF l_is_verified AND l_timestamp_berakhir < CURRENT_TIMESTAMP THEN
        -- Ubah status langganan menjadi Non Premium
        UPDATE akun
        SET is_verified = FALSE
        WHERE email = email_param;

        -- Hapus email dari tabel premium
        DELETE FROM premium
        WHERE email = email_param;

        -- Tambahkan email ke tabel nonpremium
        INSERT INTO nonpremium(email)
        VALUES (email_param);
    END IF;
END;
$$ LANGUAGE plpgsql;