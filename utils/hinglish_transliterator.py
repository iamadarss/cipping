"""Devanagari to Romanized Hinglish Transliterator for Up Clip Studio Caption Studio."""

import re

# Independent Vowels
_VOWELS = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
    'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah'
}

# Dependent Vowel Signs (Matras)
_MATRAS = {
    'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
    'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    '्': ''  # Virama / halant suppresses inherent 'a'
}

# Consonants
_CONSONANTS = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
    'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'क़': 'q', 'ख़': 'kh', 'ग़': 'gh', 'ज़': 'z', 'ड़': 'r', 'ढ़': 'rh', 'फ़': 'f'
}

_MODIFIERS = {
    'ं': 'n', 'ँ': 'n', 'ः': 'h', '़': ''
}


def devanagari_to_hinglish(text: str) -> str:
    """
    Phonetically transliterates Devanagari Hindi text to Roman/Latin characters (Hinglish).
    Converts Hindi speech into natural Roman letters, e.g.:
    "मुझे वीडियो बनाना है" -> "Mujhe video banana hai".
    Leaves non-Devanagari characters untouched.
    """
    if not text:
        return ""

    has_devanagari = any(0x0900 <= ord(c) <= 0x097F for c in text)
    if not has_devanagari:
        return text

    words = text.split()
    transliterated_words = []

    for word in words:
        w_chars = []
        i = 0
        n = len(word)
        while i < n:
            ch = word[i]

            # 2-character nukta forms
            if i + 1 < n and word[i:i+2] in _CONSONANTS:
                cons_code = _CONSONANTS[word[i:i+2]]
                i += 2
                if i < n and word[i] in _MATRAS:
                    m = _MATRAS[word[i]]
                    w_chars.append(cons_code + m)
                    i += 1
                elif i == n:
                    w_chars.append(cons_code)
                else:
                    w_chars.append(cons_code + 'a')
                continue

            if ch in _VOWELS:
                w_chars.append(_VOWELS[ch])
                i += 1
            elif ch in _CONSONANTS:
                cons_code = _CONSONANTS[ch]
                i += 1
                if i < n and word[i] in _MATRAS:
                    m = _MATRAS[word[i]]
                    w_chars.append(cons_code + m)
                    i += 1
                elif i < n and word[i] in _MODIFIERS:
                    mod = _MODIFIERS[word[i]]
                    w_chars.append(cons_code + 'a' + mod)
                    i += 1
                elif i == n:
                    # Hindi word-final schwa deletion (e.g. 'k' not 'ka')
                    w_chars.append(cons_code)
                else:
                    # Inherent 'a'
                    w_chars.append(cons_code + 'a')
            elif ch in _MODIFIERS:
                w_chars.append(_MODIFIERS[ch])
                i += 1
            elif ch in _MATRAS:
                w_chars.append(_MATRAS[ch])
                i += 1
            else:
                w_chars.append(ch)
                i += 1

        trans_word = "".join(w_chars)
        # Normalize double 'a's that often look awkward in casual Roman Hindi
        trans_word = re.sub(r'aa', 'a', trans_word)
        # Common phonetic touchups
        trans_word = re.sub(r'veediyo|vidiyo', 'video', trans_word, flags=re.IGNORECASE)
        transliterated_words.append(trans_word)

    result = " ".join(transliterated_words)
    # Capitalize first letter of sentence
    if result and result[0].isalpha():
        result = result[0].upper() + result[1:]
    return result


# Standard alias for backward compatibility
transliterate_devanagari_to_hinglish = devanagari_to_hinglish

