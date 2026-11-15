# UpClip Studio — कमियों की पूरी सूची और Antigravity मास्टर प्रॉम्प्ट

तारीख: 15 नवंबर 2026
आधार: UpClipStudio_Final_Delivery.zip (116 .py, ~31k Python लाइनें; ~43k लाइनें HTML/JS/CSS) और UPCLIP_VISUAL_AUDIT.zip (129 स्क्रीनशॉट)

## सीमाएँ (ईमानदारी से)
- ऐप चलाया नहीं गया। PyTorch/Whisper जैसी भारी डिपेंडेंसी यहाँ नहीं थीं, इसलिए टेस्ट भी नहीं चले।
- कोड पर ruff, bandit, compileall, और अपनी लिखी "टेम्पलेट/स्टैटिक/JS-फ़ेच बनाम Flask-रूट" मिलान स्क्रिप्ट चलाई। सबसे बड़ी फ़ाइलें (routes/*.py, main.js, editor.js) के चुने हुए हिस्से हाथ से पढ़े। सारी 31k लाइनें लाइन-दर-लाइन नहीं पढ़ी गईं।
- 129 में से लगभग 20 स्क्रीनशॉट पूरे आकार में देखे, बाकी कॉन्टैक्ट शीट पर।
- हर मद पर "पक्का / संभावित" का निशान है।

## A. पक्की कमियाँ (कोड में पुष्टि हुई)

| # | गंभीरता | कमी | कहाँ | असर |
|---|---|---|---|---|
| A1 | उच्च | एडिटर की ~34 `fetch('/api/editor/...')` कॉल गलत पाथ पर जाती हैं। बैकएंड `editor_bp` का `url_prefix="/editor"` है, इसलिए असली पाथ `/editor/api/editor/...` है। सिर्फ़ ~4 कॉल सही पाथ पर हैं। | static/js/editor.js (जैसे लाइन 2961, 3509, 4173), routes/editor.py:15 | templates, presets, brand-kit, render-queue, copilot, media-library, graphics, diagnostics आदि 404 देते हैं। एडिटर का बड़ा हिस्सा टूटा है। |
| A2 | उच्च | `video_to_load` असाइन होने (लाइन 66) से पहले लाइन 53 पर इस्तेमाल होता है। `UnboundLocalError` को `except Exception: pass` निगल जाता है। | routes/caption_studio.py:53 | सेव किए प्रोजेक्ट का वीडियो कैप्शन स्टूडियो में अपने-आप कभी नहीं लौटता, और कोई एरर नहीं दिखता। |
| A3 | उच्च | 5 AI टॉगल सेटिंग्स से पढ़े जाते हैं पर कहीं इस्तेमाल नहीं होते: `emotion_detection_enabled`, `min_viral_score`, `audio_normalization_enabled`, `contextual_emoji_enabled`, `broll_enabled`। | routes/process.py:206, 208, 210, 312, 313 | UI में "ON" दिखता है पर बंद करने या बदलने से कुछ नहीं बदलता। यूज़र को गलत भरोसा मिलता है। |
| A4 | उच्च | "Fast GPU Processing" बैज हार्ड-कोडेड है। `torch==2.13.0` बिना CUDA इंडेक्स के है और `scripts/setup_env.bat` सादा `pip install -r requirements.txt` करती है, इसलिए Windows पर CPU बिल्ड (`+cpu`) आता है। `config.USE_GPU = True` भी है। | templates/index.html:190, requirements.txt, scripts/setup_env.bat, config.py:132 | GPU का झूठा दावा। असल में CPU पर चलता है और Whisper धीमा रहेगा। |
| A5 | मध्यम | डायग्नोस्टिक "Hardware accelerated pixel delta verified" असल में 10×10 पिक्सल की `cv2.absdiff` है। यह CPU पर चलती है, GPU का कोई टेस्ट नहीं है। | routes/settings.py:925-935 | डायग्नोस्टिक्स भ्रामक "WORKING" दिखाता है। |
| A6 | मध्यम | `requirements.txt` में टकराव और ढीलापन: `ffmpeg==1.4` और `ffmpeg-python` दोनों `ffmpeg` मॉड्यूल देते हैं (टकराते हैं); `opencv-python` और `opencv-contrib-python` साथ में; `Flask-SQLAlchemy`, google-* और `scipy` बिना वर्ज़न के; `pyrefly` (डेव टूल) और `customtkinter` भी इंस्टॉल होते हैं। | requirements.txt | इंस्टॉल अनिश्चित, कभी `import cv2` / `import ffmpeg` अजीब तरह टूट सकता है। |
| A7 | मध्यम | टेस्ट/सैंपल वीडियो बेकार हैं: `input/sample.mp4` = 1,477 बाइट, `test_custom_settings_video.mp4` = 16 बाइट, `static/uploads/brolls/*.mp4` = 112 बाइट प्रति फ़ाइल (16 फ़ाइलें)। | input/, static/uploads/brolls/ | ऑडिट में काले "X" थंबनेल और "0:00" इसी से आए। B-roll फ़ीचर असली क्लिप से टेस्ट ही नहीं हुआ। |
| A8 | मध्यम | `app.py` में पुरानी CLI `main()` है (sample.mp4 पर चलती है) और ऊपर के स्तर पर भारी इम्पोर्ट (Whisper, scene detector आदि) हैं। `__main__` में `debug=True` है (Werkzeug डीबगर)। | app.py:47-58, 68-275, 391 | धीमा स्टार्टअप, डेड कोड, और अगर यह रास्ता चलाया गया तो डीबगर से कोड-एक्ज़ीक्यूशन का जोखिम (127.0.0.1 पर बँधा है, इसलिए कम)। |
| A9 | मध्यम | कमज़ोर `SECRET_KEY` हार्ड-कोडेड है: `"ai-shorts-studio-secret-key-change-me"` | config.py:76 | सेशन कुकी की सुरक्षा कमज़ोर। |
| A10 | मध्यम | कोई एरर हैंडलर नहीं (404/500)। सादा Flask का सफ़ेद पेज दिखता है। | app.py (कोई `errorhandler` नहीं) | ऐप की थीम से टूटा अनुभव। |
| A11 | मध्यम | Settings टैब बार का स्क्रॉलबार छिपा दिया गया है (`::-webkit-scrollbar{display:none}`) और कोई स्क्रॉल-संकेत नहीं है, इसलिए आख़िरी टैब "Diagnostics" कटकर दिखता है। | templates/settings.html:51-62 | 12 टैब में से कुछ दिखते ही नहीं। |
| A12 | मध्यम | `static/js/caption_studio.js` (4080 लाइनें) कहीं लोड नहीं होता। टेम्पलेट सिर्फ़ `js/caption_studio/caption_studio.js` (3797 लाइनें) लोड करता है। दोनों में ~7600 लाइनों का अंतर है। साथ में `caption_studio/` (React/TSX सोर्स) और `static/caption-studio/` (उसका बिल्ड) भी किसी टेम्पलेट/रूट से नहीं जुड़े। | static/js/, caption_studio/, static/caption-studio/ | तीन कैप्शन स्टूडियो कोडबेस। किसे ठीक करना है, यह भ्रम; बग गलत फ़ाइल में ठीक हो सकता है। |
| A13 | कम | साइडबार लेबल असंगत: कैप्शन स्टूडियो में "Help & Guide", बाकी 8 पेजों पर "How to Use"। | templates/caption_studio.html:117 | UI असंगति। |
| A14 | कम | `.wizard-nav` में `justify-content: space-between` है। स्टेप 1 पर "Back" छिपा है, इसलिए "Continue" बटन अकेला बाईं ओर खिसकता है। | templates/index.html:1459, style.css:1177 | बटन का गलत संरेखण। |
| A15 | कम | 276 जगह `except Exception` (blind except), जो एरर निगल जाते हैं। 38 अप्रयुक्त/अनसाइन वेरिएबल (ai_copilot.py में 7, जैसे `clips`, `audio_tracks`, `playhead_time`)। | पूरे कोडबेस में | असली बग छिप जाते हैं (A2 जैसे)। AI Copilot एडिटर की स्थिति असल में पढ़ता ही नहीं। |
| A16 | कम | `youtube.py` में 7 जगह f-string से SQL बनता है (`UPDATE ... SET {…}`, `DELETE FROM {table}`)। टेबल/कॉलम नाम कोड के तय हैं, इसलिए अभी इंजेक्शन नहीं दिखता, पर पैटर्न खतरनाक है। साथ में `urlopen` के स्कीम बिना जाँचे हैं (broll.py, settings.py, download.py) और `xml.etree` से बाहरी XML पार्स होता है। | routes/youtube.py:1283, 1883, 2131, 2188, 2273, 2708, 2725; download.py:526 | कम जोखिम, पर कठोर बनाना चाहिए। |
| A17 | कम | `data/` में असली यूज़र डेटा आ गया: `youtube.db` में 44 schedules, 38 upload_queue, 14 videos; `app.db` में 20 projects। टोकन खाली हैं (अच्छा), पर यह सोर्स ज़िप में नहीं होना चाहिए। | data/ | निजी डेटा लीक होने का जोखिम और भ्रम। |
| A18 | कम | `Project.query.get()` SQLAlchemy 2.x में पुराना (legacy) है। | routes/caption_studio.py:28 | भविष्य में टूटेगा। |

## B. ऑडिट की रिपोर्ट के दावे जो सही नहीं निकले
- "127/127 PASSED (100%)" का मतलब सिर्फ़ यह कि स्क्रिप्ट ने स्क्रीनशॉट खींच लिए। यह फ़ंक्शनल जाँच नहीं है।
- "Cloud YouTube Upload: Configured & Available" गलत है। असल में `client_secrets.json` और OAuth चाहिए।
- रिपोर्ट में "CUDA: Working / CPU Fallback" है, जबकि स्क्रीन पर "NOT SUPPORTED" है।
- "1:1 Square" बैज वाले 201×201 पिक्सल के "X" थंबनेल को "16:9 landscape preview" कहा गया।
- पैकेजिंग की वैलिडेशन रिपोर्ट में एक टेस्ट फ़ेल है (`test_home.py::test_core_routes_and_upload_work`), और बाकी 98 टेस्ट फ़ंक्शन चले ही नहीं। उसे "PASSED & DEVELOPMENT-READY" लिखना ठीक नहीं।
- मेरी पिछली बात का सुधार: स्क्रीनशॉट में स्टेपर हर जगह "01" पर और बटन हर जगह "Continue to AI Clip Settings" दिखा। कोड (`setStep`, main.js ~1827-1900) में दोनों सही बदलते हैं। इसलिए यह संभवतः ऑडिट स्क्रिप्ट की वजह से है, जिसने पैनल सीधे दिखाए। यह ऐप का बग नहीं भी हो सकता; असली वर्कफ़्लो चलाकर पुष्टि करनी होगी।

## C. संभावित (स्क्रीनशॉट पर दिखा, कोड से पक्का नहीं हुआ)
- मोबाइल (390px) हेडर टूटता है ("Up Clip Studio" तीन लाइनों में, सर्च बॉक्स चार लाइनों में), स्टेपर सिर्फ़ 3 स्टेप दिखाता है, Settings में "Reset Defaults" कटता है। style.css में सिर्फ़ 13 media query हैं।
- 1280×720 पर कैप्शन स्टूडियो का "Caption Styling" हेडर टूटता है, फ़ॉन्ट साइज़ की वैल्यू और प्रीसेट टैब ("Lou…") कटते हैं।
- मोबाइल पर "Loading your Studio…" टेक्स्ट अपलोड बॉक्स के साथ दिखता रहा (HTML में `hidden` है; `main.js:1949-1952` उसे दिखाता/छिपाता है। चलाकर पुष्टि चाहिए कि यह छिपता है)।
- बहुत छोटा, कम कंट्रास्ट वाला टेक्स्ट और चौड़ी स्क्रीन पर खाली जगह।
- "Up to 1 GB" की सीमा (`MAX_CONTENT_LENGTH`) लंबे वीडियो के लिए कम है।
- पूरा ऑडिट एक्सटेंशन के बिना 1 KB जैसे नकली वीडियो पर बना है, इसलिए क्लिप जनरेशन, कैप्शन की सटीकता और रेंडर की स्पीड अभी तक किसी ने नहीं जाँची।

## D. Antigravity के लिए मास्टर प्रॉम्प्ट
```text
ROLE
You are a senior Flask + frontend engineer. Fix defects in the UpClip Studio source (Flask blueprints, vanilla JS, Whisper/OpenCV/FFmpeg pipeline). Work in the project root. Do NOT redesign the app, rename routes, or change processing algorithms beyond what a fix below requires. Make small, reviewable changes. After EVERY phase: run the verification listed for it, show the command output, and stop if anything fails. Never claim a fix works unless you ran it. Never mark a phase done on "looks right".

PHASE 0 - BASELINE (no code changes)
0.1 Create a venv, install requirements, run `python -m compileall -q .` and `python -m pytest -q`. Record which tests pass/fail in BASELINE.md. Known: tests/test_home.py::test_core_routes_and_upload_work fails; 98 other tests were never run.
0.2 Run `ruff check --select F821,F841,E722,BLE001,B904 .` and `bandit -r . -x ./caption_studio,./tests -ll`. Save the output.

PHASE 1 - BROKEN EDITOR API PATHS (highest impact)
Problem: routes/editor.py defines editor_bp with url_prefix="/editor", so real URLs are /editor/api/editor/... . static/js/editor.js calls ~34 URLs as /api/editor/... (no /editor prefix), e.g. templates, presets, brand-kit, ready-check, render-queue/*, copilot/*, media/*, graphics/*, cache, diagnostics, fonts, project/package. These return 404. ~4 calls already use the correct prefix.
Fix: add ONE constant at the top of editor.js (const EDITOR_API = '/editor/api/editor';) and route every fetch through it. Do not add duplicate unprefixed routes on the backend. Check each endpoint actually exists in routes/editor.py (e.g. /api/editor/fonts, /api/editor/audio/diagnostics have no matching route - either add the backend route or remove the dead call and its UI).
Verify: write a script that parses all fetch() URLs in static/js/*.js and templates/*.html, normalises <param> segments, and asserts each one matches a registered Flask rule (use app.url_map). Zero unmatched allowed. Add it as tests/test_frontend_routes.py.

PHASE 2 - SILENT BUGS IN PYTHON
2.1 routes/caption_studio.py ~line 53: `video_to_load` is read before it is assigned (assigned ~line 66) and the UnboundLocalError is swallowed by `except Exception: pass`. Move the "Resolve video source" assignment above the editor_state block, and log (do not silently pass) exceptions. Add a test: a project whose editor_state has video_filename must open Caption Studio with that video.
2.2 routes/process.py ~206-210, 312-313: emotion_detection_enabled, min_viral_score, audio_normalization_enabled, contextual_emoji_enabled, broll_enabled are read but never used. Wire each into the pipeline where the matching module exists (ai/emotion_detector.py, ai/viral_score.py/clip_ranker.py threshold, ai/audio_mixer.py or utils/audio_utils.py normalization, ai/emoji_captions.py, ai/broll.py). If a feature genuinely cannot be wired, REMOVE its toggle from the UI instead of leaving a dead control. Add tests that flipping each toggle changes behavior (use mocks).
2.3 core/ai_copilot.py lines ~79-84, 273: editor state values (clips, audio_tracks, audio_clips, graphics, selected_clip_id, playhead_time, music_track) are extracted and ignored. Either use them in the copilot context or delete them.
2.4 Replace the 276 `except Exception: pass`/blind excepts in the top 10 largest route files with specific exceptions or at least logger.exception(...). Do not change behavior otherwise.
2.5 Replace Project.query.get(id) with db.session.get(Project, id).
Verify: ruff F821/F841 count must be 0 for non-test code; pytest green.

PHASE 3 - FALSE CLAIMS (GPU)
3.1 Remove the hard-coded "Fast GPU Processing" pill in templates/index.html (~line 190). Replace with a pill driven by a real endpoint, e.g. /api/settings/hardware returning torch.cuda.is_available(); show "GPU (CUDA)" or "CPU mode".
3.2 routes/settings.py ~925-935: remove "(Hardware accelerated pixel delta verified)". Scene detection check is a CPU cv2.absdiff on a 10x10 array. Report CUDA/GPU status honestly and keep CPU fallback as "Working (CPU)", not "NOT SUPPORTED"+"WORKING" mixed signals.
3.3 requirements: torch/torchaudio/torchvision pinned without a CUDA index install CPU-only builds on Windows. Add requirements-gpu.txt (with --extra-index-url https://download.pytorch.org/whl/cuXXX) and document it in README; make scripts/setup_env.bat/.sh detect an NVIDIA GPU (nvidia-smi) and choose the right file. Set config.USE_GPU from real detection, not a constant True.

PHASE 4 - DEPENDENCIES
4.1 requirements.txt: remove `ffmpeg==1.4` (conflicts with ffmpeg-python on the `ffmpeg` module name); keep only one of opencv-python / opencv-contrib-python (check whether cv2.ximgproc/contrib APIs are used first); pin Flask-SQLAlchemy, google-auth-*, google-api-python-client, scipy; move pyrefly to requirements-dev.txt; verify whether customtkinter is only needed by desktop_launcher.py.
4.2 Add pip check to setup scripts. Verify in a clean venv: `pip install -r requirements.txt && python -c "import cv2, whisper, flask, ffmpeg"`.

PHASE 5 - FRONTEND / UX
5.1 Add @app.errorhandler(404) and (500): JSON for /api/* and /editor/api/*, a themed HTML page (same dark theme, sidebar, "Back to Home") for pages.
5.2 Settings tabs (templates/settings.html ~51-62): stop hiding the scrollbar; add edge fade + prev/next arrows, or wrap tabs. All 12 tabs must be reachable at 1280px and 390px.
5.3 Sidebar label: make caption_studio.html say "How to Use" like every other page (or change all to one name).
5.4 .wizard-nav: use margin-left:auto on #wizNext (or flex-end) so the button is right-aligned when Back is hidden.
5.5 Mobile (<=480px): header must not wrap the logo or search into 3-4 lines (hide the search text, icon only; shorten "UpClip Studio"); wizard stepper must scroll horizontally with all 5 steps reachable or collapse to "Step 2 of 5"; Caption Styling header buttons must wrap, not clip; settings Reset Defaults must not be cut off. At 1280x720 the Caption Studio right panel header and preset tabs (Loud Captions) must not clip.
5.6 Confirm #studioLoader ("Loading your Studio...") is hidden by default and never visible after load on mobile.
5.7 Raise the smallest text (about 10-11px) to 12px+ and fix low-contrast greys to meet WCAG AA.
5.8 Explain the 1 GB upload limit in the UI text or make MAX_CONTENT_LENGTH configurable in Settings.
Verify with Playwright screenshots at 1920x1080, 1366x768, 1280x720, 768x1024, 390x844 for: Home, AI Clip Studio (all 5 real wizard steps reached by clicking, not by forcing DOM), Caption Studio, Settings (every tab), Downloader. Save to audit_after/ and compare with the original UPCLIP_VISUAL_AUDIT.

PHASE 6 - SECURITY
6.1 app.py: delete the legacy CLI main() (sample.mp4 pipeline) or move it to scripts/legacy_cli.py; remove heavy top-level imports so `python app.py` starts fast; use debug=False.
6.2 config.SECRET_KEY: read from env/.env, and generate+persist a random key on first run in the data directory if missing. Never ship a default.
6.3 routes/youtube.py SQL f-strings (lines ~1283, 1883, 2131, 2188, 2273, 2708, 2725): use fixed allow-lists of column/table names and assert membership before building the query.
6.4 urlopen calls (ai/broll.py, routes/settings.py, routes/download.py, utils/hinglish_transliterator.py): allow only http/https. routes/download.py ~526: parse XML with defusedxml.
6.5 Add path-traversal tests for every route that takes a filename (download, thumbnail, upload, stream).

PHASE 7 - DEAD CODE AND PACKAGING
7.1 Prove which Caption Studio is live. Templates load only static/js/caption_studio/caption_studio.js. static/js/caption_studio.js (4080 lines), caption_studio/ (React/TSX) and static/caption-studio/ (built bundle) are not referenced. Confirm by grep, then move them to _archive/ (do not delete) and note it in CHANGELOG.md.
7.2 Remove user data from the source package: data/youtube.db, data/app.db, data/*.json, logs, input/*.mp4, static/uploads/brolls/*. Keep empty folders with .gitkeep. Ensure the app creates DBs on first run.
7.3 Replace the 1.4 KB input/sample.mp4 and the 112-byte broll files with a generated 5-10 s test clip made by ffmpeg (testsrc + sine) for tests only, in tests/fixtures/. Do not ship it in the product.
7.4 Verify packaging/UpClipStudio.spec still builds (`packaging/build_executable.bat`) and the exe starts, serves /, and shows /settings diagnostics.

PHASE 8 - END-TO-END PROOF
Using a REAL 60-120 s spoken video with Hindi/English/Hinglish speech: run the full flow upload -> settings -> generate -> review -> export. Confirm: transcript is produced, clips are listed in "Generated Clips" (not empty), captions are burned in, the output plays. Test every one of the 24 caption presets on a real frame and save one screenshot each. Fix any failure you find, then rerun.

DELIVERABLES
1. All fixes as git commits, one commit per phase.
2. FIXES.md: for each item - file, line, what was wrong, what changed, how you verified (command + output).
3. pytest and ruff output at the end (target: 0 F821, all tests passing or each failure explained).
4. audit_after/ screenshots.
5. An honest "NOT VERIFIED" list for anything you could not run.
```
