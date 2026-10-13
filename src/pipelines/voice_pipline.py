from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import os
import librosa
import streamlit as st
import io

@st.cache_resource

def load_voice_encoder():
    return VoiceEncoder()

def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        Wav = preprocess_wav(audio, source_sr=sr)
        embedding = encoder.embed_utterance(Wav)

        return embedding.tolist()

    except Exception as e:
        st.error('Voice recog error')
        return None

def identify_speaker(new_embedding, candicates_dict,threshold=0.65):
    if new_embedding is None or not candicates_dict:
        return None,0.0

    best_sid = None 
    best_score = -1.0

    for sid, stored_embedding in candicates_dict.item():
        if stored_embedding:
            similarity = np.dot(new_embedding,stored_embedding)
            if similarity > best_score:
                best_score = similarity
                best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score

    return None, best_score
def process_bulk_audio(audio_bytes,candidates_dict,threshold=0.65):

    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(io.BytesIO(audio_bytes),sr=16000)
        segments = librosa.effects.split(audio,top_db=25)

        identified_results = {}

        for start,end in segments:

            if(end-start) < sr* 0.5:
                continue
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterence(wav)

            sid,score = identify_speaker(embedding,candidates_dict, threshold)
            if sid:
                if sid not in identify_results or score >identified_results[sid]:
                    identified_results[sid] = score

        return identified_results

    except Exception as e:
        st.error('Bulk process error')
        return{}      
