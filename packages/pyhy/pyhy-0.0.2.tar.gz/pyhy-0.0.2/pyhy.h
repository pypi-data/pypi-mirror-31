#pragma once

#define HYDRO_VERSION_MAJOR 1
#define HYDRO_VERSION_MINOR 0
/* ---------------- */
int hydro_init(void);

/* ---------------- */
#define hydro_random_SEEDBYTES 32
uint32_t hydro_random_u32(void);
uint32_t hydro_random_uniform(const uint32_t upper_bound);
void hydro_random_buf(void *out, size_t out_len);
void hydro_random_buf_deterministic(void *out, size_t out_len, const uint8_t seed[hydro_random_SEEDBYTES]);
void hydro_random_ratchet(void);
void hydro_random_reseed(void);
/* ---------------- */

/* ---------------- */
#define hydro_hash_BYTES 32
#define hydro_hash_BYTES_MAX 65535
#define hydro_hash_BYTES_MIN 16
#define hydro_hash_CONTEXTBYTES 8
#define hydro_hash_KEYBYTES 32

typedef struct hydro_hash_state {
    uint32_t state[12];
    uint8_t  buf_off;
    uint8_t  align[3];
} hydro_hash_state;

void hydro_hash_keygen(uint8_t key[hydro_hash_KEYBYTES]);
int hydro_hash_init(hydro_hash_state *state, const char ctx[hydro_hash_CONTEXTBYTES], const uint8_t key[hydro_hash_KEYBYTES]);
int hydro_hash_update(hydro_hash_state *state, const void *in_, size_t in_len);
int hydro_hash_final(hydro_hash_state *state, uint8_t *out, size_t out_len);
int hydro_hash_hash(uint8_t *out, size_t out_len, const void *in_, size_t in_len, const char    ctx[hydro_hash_CONTEXTBYTES], const uint8_t key[hydro_hash_KEYBYTES]);
/* ---------------- */

/* ---------------- */
#define hydro_secretbox_CONTEXTBYTES 8
#define hydro_secretbox_HEADERBYTES  36
#define hydro_secretbox_KEYBYTES     32
#define hydro_secretbox_PROBEBYTES   16
void hydro_secretbox_keygen(uint8_t key[hydro_secretbox_KEYBYTES]);
int hydro_secretbox_encrypt(uint8_t *c, const void *m_, size_t mlen, uint64_t msg_id, const char ctx[hydro_secretbox_CONTEXTBYTES], const uint8_t key[hydro_secretbox_KEYBYTES]);
int hydro_secretbox_decrypt(void *m_, const uint8_t *c, size_t clen, uint64_t msg_id, const char ctx[hydro_secretbox_CONTEXTBYTES], const uint8_t key[hydro_secretbox_KEYBYTES]);
void hydro_secretbox_probe_create(uint8_t probe[hydro_secretbox_PROBEBYTES], const uint8_t *c, size_t c_len, const char ctx[hydro_secretbox_CONTEXTBYTES], const uint8_t key[hydro_secretbox_KEYBYTES]);
int hydro_secretbox_probe_verify(const uint8_t probe[hydro_secretbox_PROBEBYTES], const uint8_t *c, size_t c_len, const char ctx[hydro_secretbox_CONTEXTBYTES], const uint8_t key[hydro_secretbox_KEYBYTES]);
/* ---------------- */

/* ---------------- */
#define hydro_kdf_CONTEXTBYTES 8
#define hydro_kdf_KEYBYTES 32
#define hydro_kdf_BYTES_MAX 65535
#define hydro_kdf_BYTES_MIN 16
void hydro_kdf_keygen(uint8_t key[hydro_kdf_KEYBYTES]);
int hydro_kdf_derive_from_key(uint8_t *subkey, size_t subkey_len, uint64_t subkey_id, const char ctx[hydro_kdf_CONTEXTBYTES], const uint8_t key[hydro_kdf_KEYBYTES]);
/* ---------------- */

/* ---------------- */
#define hydro_sign_BYTES          64
#define hydro_sign_CONTEXTBYTES   8
#define hydro_sign_PUBLICKEYBYTES 32
#define hydro_sign_SECRETKEYBYTES 64
#define hydro_sign_SEEDBYTES      32

typedef struct hydro_sign_state {
    hydro_hash_state hash_st;
} hydro_sign_state;

typedef struct hydro_sign_keypair {
    uint8_t pk[hydro_sign_PUBLICKEYBYTES];
    uint8_t sk[hydro_sign_SECRETKEYBYTES];
} hydro_sign_keypair;

void hydro_sign_keygen(hydro_sign_keypair *kp);
void hydro_sign_keygen_deterministic(hydro_sign_keypair *kp, const uint8_t seed[hydro_sign_SEEDBYTES]);
int hydro_sign_init(hydro_sign_state *state, const char ctx[hydro_sign_CONTEXTBYTES]);
int hydro_sign_update(hydro_sign_state *state, const void *m_, size_t mlen);
int hydro_sign_final_create(hydro_sign_state *state, uint8_t csig[hydro_sign_BYTES], const uint8_t sk[hydro_sign_SECRETKEYBYTES]);
int hydro_sign_final_verify(hydro_sign_state *state, const uint8_t csig[hydro_sign_BYTES], const uint8_t pk[hydro_sign_PUBLICKEYBYTES]);
int hydro_sign_create(uint8_t csig[hydro_sign_BYTES], const void *m_, size_t mlen,  const char ctx[hydro_sign_CONTEXTBYTES], const uint8_t sk[hydro_sign_SECRETKEYBYTES]);
int hydro_sign_verify(const uint8_t csig[hydro_sign_BYTES], const void *m_, size_t mlen, const char ctx[hydro_sign_CONTEXTBYTES], const uint8_t pk[hydro_sign_PUBLICKEYBYTES]);
/* ---------------- */

/* ---------------- */
#define hydro_pwhash_CONTEXTBYTES 8
#define hydro_pwhash_MASTERKEYBYTES 32
#define hydro_pwhash_STOREDBYTES 128

void hydro_pwhash_keygen(uint8_t master_key[hydro_pwhash_MASTERKEYBYTES]);
int hydro_pwhash_deterministic(uint8_t *h, size_t h_len, const char *passwd, size_t passwd_len, const char ctx[hydro_pwhash_CONTEXTBYTES], const uint8_t master_key[hydro_pwhash_MASTERKEYBYTES], uint64_t opslimit, size_t memlimit, uint8_t threads);
int hydro_pwhash_create(uint8_t stored[hydro_pwhash_STOREDBYTES], const char *passwd, size_t passwd_len, const uint8_t master_key[hydro_pwhash_MASTERKEYBYTES], uint64_t opslimit, size_t memlimit, uint8_t threads);
int hydro_pwhash_verify(const uint8_t stored[hydro_pwhash_STOREDBYTES], const char *passwd, size_t passwd_len, const uint8_t master_key[hydro_pwhash_MASTERKEYBYTES], uint64_t opslimit_max, size_t memlimit_max, uint8_t threads_max);
int hydro_pwhash_derive_static_key(uint8_t *static_key, size_t static_key_len, const uint8_t stored[hydro_pwhash_STOREDBYTES], const char *passwd, size_t passwd_len, const char ctx[hydro_pwhash_CONTEXTBYTES], const uint8_t master_key[hydro_pwhash_MASTERKEYBYTES], uint64_t opslimit_max, size_t memlimit_max, uint8_t threads_max);
int hydro_pwhash_reencrypt(uint8_t stored[hydro_pwhash_STOREDBYTES], const uint8_t master_key[hydro_pwhash_MASTERKEYBYTES], const uint8_t new_master_key[hydro_pwhash_MASTERKEYBYTES]);
int hydro_pwhash_upgrade(uint8_t stored[hydro_pwhash_STOREDBYTES], const uint8_t master_key[hydro_pwhash_MASTERKEYBYTES], uint64_t opslimit, size_t memlimit, uint8_t threads);

/* ---------------- */
void hydro_memzero(void *pnt, size_t len);
void hydro_increment(uint8_t *n, size_t len);
bool hydro_equal(const void *b1_, const void *b2_, size_t len);
int hydro_compare(const uint8_t *b1_, const uint8_t *b2_, size_t len);
char *hydro_bin2hex(char *hex, size_t hex_maxlen, const uint8_t *bin, size_t bin_len);
int hydro_hex2bin(uint8_t *bin, size_t bin_maxlen, const char *hex, size_t hex_len, const char *ignore, const char **hex_end_p);
int hydro_pad(unsigned char *buf, size_t unpadded_buflen, size_t blocksize, size_t max_buflen);
int hydro_unpad(const unsigned char *buf, size_t padded_buflen, size_t blocksize);
/* ---------------- */


/* ---------------- */
