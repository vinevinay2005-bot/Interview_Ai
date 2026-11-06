"""
Speech Interaction Helper Module
Provides:
1. Browser-based Text-to-Speech (TTS) using Web Speech Synthesis API
2. Browser-based Speech-to-Text (STT) using Web Speech Recognition API
3. Audio control widgets seamlessly embeddable in Streamlit
"""

import streamlit.components.v1 as components

def render_tts_player(text_to_speak: str, element_id: str = "tts_player"):
    """
    Renders an interactive audio player widget that speaks the provided text
    using the browser's native Web Speech Synthesis API.
    """
    # Sanitize text for JavaScript string literal
    safe_text = text_to_speak.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", " ")

    html_code = f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 12px 18px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="background: #3b82f6; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white;">
                🔊
            </div>
            <div>
                <div style="font-weight: 600; font-size: 13px; color: #f1f5f9;">AI Voice Interviewer</div>
                <div style="font-size: 11px; color: #94a3b8;" id="tts_status_{element_id}">Click listen to hear question</div>
            </div>
        </div>
        <div style="display: flex; gap: 8px;">
            <button id="btn_speak_{element_id}" onclick="speakText_{element_id}()" style="background: #2563eb; color: white; border: none; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 500; cursor: pointer; transition: background 0.2s;">
                ▶ Listen Out Loud
            </button>
            <button id="btn_stop_{element_id}" onclick="stopSpeaking_{element_id}()" style="background: #475569; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;">
                ⏹ Stop
            </button>
        </div>
    </div>

    <script>
    var text_{element_id} = "{safe_text}";
    var synth_{element_id} = window.speechSynthesis;

    function speakText_{element_id}() {{
        if (!('speechSynthesis' in window)) {{
            document.getElementById('tts_status_{element_id}').innerText = 'Speech Synthesis not supported in this browser.';
            return;
        }}
        synth_{element_id}.cancel(); // Stop any pending speech
        var utterance = new SpeechSynthesisUtterance(text_{element_id});
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        
        // Pick high-quality English voice if available
        var voices = synth_{element_id}.getVoices();
        for (var i = 0; i < voices.length; i++) {{
            if (voices[i].lang.startsWith('en') && (voices[i].name.includes('Natural') || voices[i].name.includes('Google') || voices[i].name.includes('Samantha') || voices[i].name.includes('Microsoft'))) {{
                utterance.voice = voices[i];
                break;
            }}
        }}

        utterance.onstart = function() {{
            document.getElementById('tts_status_{element_id}').innerText = 'Speaking question...';
            document.getElementById('btn_speak_{element_id}').style.background = '#10b981';
        }};

        utterance.onend = function() {{
            document.getElementById('tts_status_{element_id}').innerText = 'Finished speaking';
            document.getElementById('btn_speak_{element_id}').style.background = '#2563eb';
        }};

        utterance.onerror = function() {{
            document.getElementById('tts_status_{element_id}').innerText = 'Audio playback stopped';
            document.getElementById('btn_speak_{element_id}').style.background = '#2563eb';
        }};

        synth_{element_id}.speak(utterance);
    }}

    function stopSpeaking_{element_id}() {{
        if (synth_{element_id}) {{
            synth_{element_id}.cancel();
            document.getElementById('tts_status_{element_id}').innerText = 'Stopped';
            document.getElementById('btn_speak_{element_id}').style.background = '#2563eb';
        }}
    }}
    </script>
    """
    components.html(html_code, height=75)

def render_stt_mic_helper(target_input_label: str = "Candidate Response"):
    """
    Renders an in-browser microphone dictation widget using Web Speech Recognition.
    Allows candidate to speak their response and copy the live transcription into the answer field.
    """
    html_code = f"""
    <div style="background: #1e293b; padding: 14px 18px; border-radius: 10px; border: 1px dashed #475569; margin: 10px 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span id="mic_icon" style="font-size: 18px;">🎙️</span>
                <span style="font-size: 13px; font-weight: 600; color: #f8fafc;">Voice Input Assistant (Speech-to-Text)</span>
                <span id="stt_badge" style="font-size: 11px; padding: 2px 8px; border-radius: 12px; background: #334155; color: #94a3b8;">Ready</span>
            </div>
            <div style="display: flex; gap: 8px;">
                <button id="btn_record" onclick="toggleRecording()" style="background: #0284c7; color: white; border: none; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;">
                    🔴 Start Speaking
                </button>
                <button id="btn_copy" onclick="copyTranscription()" style="background: #334155; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;">
                    📋 Copy Text
                </button>
            </div>
        </div>
        <div id="live_transcript_box" style="margin-top: 10px; min-height: 44px; max-height: 80px; overflow-y: auto; background: #0f172a; padding: 8px 12px; border-radius: 6px; font-size: 12px; color: #cbd5e1; border: 1px solid #334155;">
            <em id="placeholder_text" style="color: #64748b;">Click 'Start Speaking' to dictate your answer using your microphone. Once finished, click 'Copy Text' and paste it into the answer box below.</em>
        </div>
    </div>

    <script>
    var recognition = null;
    var isRecording = false;
    var finalTranscript = '';

    if ('webkitSpeechRecognition' in window) {{
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = function() {{
            isRecording = true;
            document.getElementById('stt_badge').innerText = 'Listening...';
            document.getElementById('stt_badge').style.background = '#dc2626';
            document.getElementById('stt_badge').style.color = '#fff';
            document.getElementById('btn_record').innerText = '⏹ Finish Recording';
            document.getElementById('btn_record').style.background = '#dc2626';
            var ph = document.getElementById('placeholder_text');
            if (ph) ph.style.display = 'none';
        }};

        recognition.onresult = function(event) {{
            var interim = '';
            for (var i = event.resultIndex; i < event.results.length; ++i) {{
                if (event.results[i].isFinal) {{
                    finalTranscript += event.results[i][0].transcript + ' ';
                }} else {{
                    interim += event.results[i][0].transcript;
                }}
            }}
            document.getElementById('live_transcript_box').innerText = finalTranscript + interim;
        }};

        recognition.onerror = function(event) {{
            document.getElementById('stt_badge').innerText = 'Error: ' + event.error;
            document.getElementById('btn_record').innerText = '🔴 Start Speaking';
            document.getElementById('btn_record').style.background = '#0284c7';
            isRecording = false;
        }};

        recognition.onend = function() {{
            isRecording = false;
            document.getElementById('stt_badge').innerText = 'Captured';
            document.getElementById('stt_badge').style.background = '#10b981';
            document.getElementById('stt_badge').style.color = '#fff';
            document.getElementById('btn_record').innerText = '🔴 Speak More';
            document.getElementById('btn_record').style.background = '#0284c7';
        }};
    }}

    function toggleRecording() {{
        if (!recognition) {{
            alert('Speech Recognition is supported in Chrome, Edge, and modern browsers. Please use the text area if your browser does not support it.');
            return;
        }}
        if (!isRecording) {{
            recognition.start();
        }} else {{
            recognition.stop();
        }}
    }}

    function copyTranscription() {{
        var text = document.getElementById('live_transcript_box').innerText;
        if (text && !text.includes("Click 'Start Speaking'")) {{
            navigator.clipboard.writeText(text).then(function() {{
                alert('Dictated text copied to clipboard! Paste it into the response box.');
            }});
        }} else {{
            alert('No speech recorded yet. Please speak into your microphone first.');
        }}
    }}
    </script>
    """
    components.html(html_code, height=130)
