"""Devanagari to Romanized Hinglish Transliterator & Urdu to Hindi/Hinglish Converter for Up Clip Studio Caption Studio."""

import re
import urllib.request
import urllib.parse
import json

# Independent Vowels (Devanagari)
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

# Consonants (Devanagari)
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

# =========================================================================
# URDU TO HINDI & HINGLISH PHONETIC MAPS
# =========================================================================

URDU_ASPIRATED_HINDI = {
    'بھ': 'भ', 'پھ': 'फ', 'تھ': 'थ', 'ٹھ': 'ठ', 'جھ': 'झ',
    'چھ': 'छ', 'دھ': 'ध', 'ڈھ': 'ढ', 'کھ': 'ख', 'گھ': 'घ',
    'رہ': 'ढ़', 'ڑھ': 'ढ़', 'نہ': 'न्ह', 'مہ': 'म्ह', 'لہ': 'ल्ह'
}

URDU_ASPIRATED_HINGLISH = {
    'بھ': 'bh', 'پھ': 'ph', 'تھ': 'th', 'ٹھ': 'th', 'جھ': 'jh',
    'چھ': 'chh', 'دھ': 'dh', 'ڈھ': 'dh', 'کھ': 'kh', 'گھ': 'gh',
    'رہ': 'rh', 'ڑھ': 'rh', 'نہ': 'nh', 'مہ': 'mh', 'لہ': 'lh'
}

URDU_CHAR_MAP_HINDI = {
    'ا': 'अ', 'آ': 'आ', 'ب': 'ब', 'پ': 'प', 'ت': 'त', 'ٹ': 'ट', 'ث': 'स',
    'ج': 'ज', 'چ': 'च', 'ح': 'ह', 'خ': 'ख़', 'د': 'द', 'ड': 'ड', 'ذ': 'ज़',
    'ر': 'र', 'ڑ': 'ड़', 'ز': 'ज़', 'ژ': 'झ़', 'س': 'स', 'ش': 'श', 'ص': 'स',
    'ض': 'ज़', 'ط': 'त', 'ظ': 'ज़', 'ع': 'अ', 'غ': 'ग़', 'ف': 'फ़', 'ق': 'क़',
    'ک': 'क', 'گ': 'ग', 'ل': 'ल', 'म': 'म', 'ن': 'न', 'ں': 'ं', 'و': 'व',
    'ہ': 'ह', 'ه': 'ह', 'ھ': 'ह', 'ء': '', 'ی': 'ी', 'ے': 'े', 'ئ': 'ई', 'ۃ': 'त',
    'ي': 'ी', 'ك': 'क', 'ى': 'ी', 'ة': 'ह', 'ؤ': 'ओ', 'إ': 'इ', 'أ': 'अ'
}

URDU_CHAR_MAP_HINGLISH = {
    'ا': 'a', 'آ': 'aa', 'ب': 'b', 'پ': 'p', 'ت': 't', 'ٹ': 't', 'ث': 's',
    'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ڈ': 'd', 'ذ': 'z',
    'ر': 'r', 'ڑ': 'r', 'ز': 'z', 'ژ': 'zh', 'س': 's', 'ش': 'sh', 'ص': 's',
    'ض': 'z', 'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
    'ک': 'k', 'گ': 'g', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ں': 'n', 'و': 'o',
    'ہ': 'h', 'ه': 'h', 'ھ': 'h', 'ء': '', 'ی': 'i', 'ے': 'e', 'ئ': 'i', 'ۃ': 't',
    'ي': 'i', 'ك': 'k', 'ى': 'i', 'ة': 'h', 'ؤ': 'o', 'إ': 'i', 'أ': 'a'
}

# High-frequency Hindustani vocabulary map for natural conversational output
URDU_WORD_DICT = {
    'اب': ('अब', 'ab'),
    'سوال': ('सवाल', 'sawal'),
    'کی': ('की', 'ki'),
    'کے': ('के', 'ke'),
    'کا': ('का', 'ka'),
    'کو': ('को', 'ko'),
    'سے': ('से', 'se'),
    'میں': ('में', 'mein'),
    'پر': ('पर', 'par'),
    'تک': ('तक', 'tak'),
    'یہ': ('यह', 'yeh'),
    'وہ': ('वह', 'woh'),
    'اس': ('इस', 'is'),
    'اسے': ('इसे', 'ise'),
    'ان': ('इन', 'in'),
    'انہیں': ('इन्हें', 'inhein'),
    'کیا': ('क्या', 'kya'),
    'کیوں': ('क्यों', 'kyun'),
    'کیسے': ('कैसे', 'kaise'),
    'کب': ('कब', 'kab'),
    'کہاں': ('कहाँ', 'kahan'),
    'کون': ('कौन', 'kaun'),
    'کہ': ('कि', 'ki'),
    'اور': ('और', 'aur'),
    'لیکن': ('लेकिन', 'lekin'),
    'مگر': ('मगर', 'magar'),
    'اگر': ('अगर', 'agar'),
    'تو': ('तो', 'to'),
    'بھی': ('भी', 'bhi'),
    'ہی': ('ही', 'hi'),
    'ہے': ('है', 'hai'),
    'ہیں': ('हैं', 'hain'),
    'تھا': ('था', 'tha'),
    'تھی': ('थी', 'thi'),
    'تھے': ('थे', 'the'),
    'ہو': ('हो', 'ho'),
    'ہوا': ('हुआ', 'hua'),
    'ہوئی': ('हुई', 'hui'),
    'ہوئے': ('हुए', 'hue'),
    'ہوتا': ('होता', 'hota'),
    'ہوتی': ('होती', 'hoti'),
    'ہوتے': ('होते', 'hote'),
    'کر': ('कर', 'kar'),
    'کرنا': ('करना', 'karna'),
    'کرنے': ('करने', 'karne'),
    'کرتا': ('करता', 'karta'),
    'کرتی': ('करती', 'karti'),
    'کرتے': ('करते', 'karte'),
    'کریں': ('करें', 'karein'),
    'کررہا': ('कर रहा', 'kar raha'),
    'کررہے': ('कर रहे', 'kar rahe'),
    'کررہی': ('कर रही', 'kar rahi'),
    'دیکھ': ('देख', 'dekh'),
    'دیکھیں': ('देखें', 'dekhein'),
    'دیکھی': ('देखिए', 'dekhiye'),
    'سمجھ': ('समझ', 'samajh'),
    'سمجھے': ('समझें', 'samjhein'),
    'سمجھنا': ('समझना', 'samajhna'),
    'کما': ('कमा', 'kama'),
    'کماتا': ('कमाता', 'kamata'),
    'کماتے': ('कमाते', 'kamate'),
    'کماتی': ('कमाती', 'kamati'),
    'دولر': ('डॉलर', 'dollar'),
    'ڈالر': ('डॉलर', 'dollar'),
    'ویڈیو': ('वीडियो', 'video'),
    'بات': ('बात', 'baat'),
    'لوگ': ('लोग', 'log'),
    'کام': ('काम', 'kaam'),
    'ایک': ('एक', 'ek'),
    'دو': ('दो', 'do'),
    'تین': ('तीन', 'teen'),
    'چار': ('चार', 'chaar'),
    'پانچ': ('पाँच', 'paanch'),
    'بہت': ('बहुत', 'bahut'),
    'زیادہ': ('ज़्यादा', 'zyada'),
    'کم': ('कम', 'kam'),
    'اچھا': ('अच्छा', 'achha'),
    'اچھی': ('अच्छी', 'achhi'),
    'اچھے': ('अच्छे', 'achhe'),
    'نہیں': ('नहीं', 'nahin'),
    'نہ': ('ना', 'na'),
    'پہلے': ('पहले', 'pehle'),
    'بعد': ('बाद', 'baad'),
    'اپنا': ('अपना', 'apna'),
    'अपनी': ('अपनी', 'apni'),
    'اپنے': ('अपने', 'apne'),
    'آپ': ('आप', 'aap'),
    'تم': ('तुम', 'tum'),
    'ہم': ('हम', 'hum'),
    'میں': ('मैं', 'main'),
    'پیسے': ('पैसे', 'paise'),
    'روپے': ('रुपये', 'rupaye'),
    'ٹائم': ('टाइम', 'time'),
    'وقت': ('वक़्त', 'waqt'),
    'لوٹ': ('लॉट', 'lot'),
}


def is_urdu_or_arabic(text: str) -> bool:
    """Check if string contains any Urdu/Arabic/Shahmukhi characters."""
    if not text:
        return False
    return any(
        0x0600 <= ord(c) <= 0x06FF or
        0x0750 <= ord(c) <= 0x077F or
        0x08A0 <= ord(c) <= 0x08FF or
        0xFB50 <= ord(c) <= 0xFDFF or
        0xFE70 <= ord(c) <= 0xFEFF
        for c in text
    )


def urdu_to_devanagari(text: str) -> str:
    """Offline phonetic converter from Urdu/Arabic script to Devanagari Hindi."""
    if not text:
        return ""
    words = text.split()
    converted = []
    for w in words:
        clean = re.sub(r'[^\w\s\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]', '', w)
        if clean in URDU_WORD_DICT:
            converted.append(URDU_WORD_DICT[clean][0])
            continue
        res = []
        i = 0
        n = len(w)
        while i < n:
            if i + 1 < n and w[i:i+2] in URDU_ASPIRATED_HINDI:
                res.append(URDU_ASPIRATED_HINDI[w[i:i+2]])
                i += 2
            elif w[i] in URDU_CHAR_MAP_HINDI:
                res.append(URDU_CHAR_MAP_HINDI[w[i]])
                i += 1
            else:
                res.append(w[i])
                i += 1
        converted.append(''.join(res))
    return ' '.join(converted)


def urdu_to_hinglish(text: str) -> str:
    """Offline phonetic converter from Urdu script directly to Roman Hinglish."""
    if not text:
        return ""
    words = text.split()
    converted = []
    for w in words:
        clean = re.sub(r'[^\w\s\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]', '', w)
        if clean in URDU_WORD_DICT:
            converted.append(URDU_WORD_DICT[clean][1])
            continue
        res = []
        i = 0
        n = len(w)
        while i < n:
            if i + 1 < n and w[i:i+2] in URDU_ASPIRATED_HINGLISH:
                res.append(URDU_ASPIRATED_HINGLISH[w[i:i+2]])
                i += 2
            elif w[i] in URDU_CHAR_MAP_HINGLISH:
                res.append(URDU_CHAR_MAP_HINGLISH[w[i]])
                i += 1
            else:
                res.append(w[i])
                i += 1
        converted.append(''.join(res))
    res_str = ' '.join(converted)
    if res_str and res_str[0].isalpha():
        res_str = res_str[0].upper() + res_str[1:]
    return res_str


def translate_online(text: str, target: str = "hi") -> str:
    """
    Fast online Google Translate request.
    Returns translated string or empty string on failure.
    """
    if not text or not text.strip():
        return text
    try:
        encoded = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target}&dt=t&q={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and data[0]:
                parts = [p[0] for p in data[0] if p and p[0]]
                return "".join(parts).strip()
    except Exception:
        pass
    return ""


def devanagari_to_hinglish(text: str) -> str:
    """
    Phonetically transliterates Devanagari Hindi text to Roman/Latin characters (Hinglish).
    Converts Hindi speech into natural Roman letters, e.g.:
    "मुझे वीडियो बनाना है" -> "Mujhe video banana hai".
    "वह कुत्ता है" -> "Vah kutta hai".
    Also automatically handles any Urdu script input by converting it first!
    """
    if not text:
        return ""

    # If text is in Urdu/Arabic script, convert it first!
    if is_urdu_or_arabic(text):
        # Try online translation to natural Hindi first
        online_hindi = translate_online(text, target="hi")
        if online_hindi and not is_urdu_or_arabic(online_hindi):
            text = online_hindi
        else:
            # Fallback to offline Urdu-to-Devanagari
            text = urdu_to_devanagari(text)

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


def convert_text_to_target_language(text: str, target_lang: str) -> str:
    """
    Universal language converter ensuring text matches target language:
    - 'hinglish': guarantees Roman English script (no Urdu, no Devanagari)
    - 'hi': guarantees Devanagari Hindi script (converts any Urdu to Hindi)
    - 'en': guarantees English translation
    """
    if not text or not text.strip():
        return text

    target = target_lang.lower().strip()

    if target in ("hinglish", "hi-latn"):
        return devanagari_to_hinglish(text)

    elif target in ("hi", "hindi"):
        if is_urdu_or_arabic(text):
            online_hi = translate_online(text, target="hi")
            if online_hi and not is_urdu_or_arabic(online_hi):
                return online_hi
            return urdu_to_devanagari(text)
        # If already Devanagari or other, return as is
        return text

    elif target in ("en", "english"):
        if is_urdu_or_arabic(text) or any(0x0900 <= ord(c) <= 0x097F for c in text):
            en_trans = translate_online(text, target="en")
            if en_trans:
                return en_trans
        return text

    return text


# Standard alias for backward compatibility
transliterate_devanagari_to_hinglish = devanagari_to_hinglish
