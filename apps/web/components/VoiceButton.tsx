"use client";

import React, { useState } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { Button } from './ui/button'; // Assuming shadcn/ui
import { toast } from 'react-hot-toast';

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
  isLoading?: boolean;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({ onTranscript, isLoading }) => {
  const [isRecording, setIsRecording] = useState(false);

  const startRecording = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        toast.error("Browser does not support audio recording");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        setIsRecording(false);
        await processAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      toast.success("Listening...");

    } catch (err) {
      console.error("Mic error:", err);
      toast.error("Could not access microphone");
    }
  };

  const stopRecording = () => {
    // In a real implementation, we would need to store the mediaRecorder ref
    // For this mock v1, we essentially simulate the toggle
    setIsRecording(false);
    toast("Recording processed (mock)");
    onTranscript("Show me the latest trading analysis for EURUSD");
  };

  const processAudio = async (blob: Blob) => {
    // Phase 22: Upload blob to /api/voice/transcribe
    // For Phase 21 Gap 5, we simulate the transcription
    console.log("Audio blob size:", blob.size);
  };

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <Button
      variant={isRecording ? "destructive" : "secondary"}
      size="icon"
      onClick={handleClick}
      disabled={isLoading}
      className={`rounded-full transition-all ${isRecording ? 'animate-pulse' : ''}`}
      aria-label={isRecording ? "Stop recording" : "Start voice command"}
    >
      {isLoading ? (
        <Loader2 className="h-5 w-5 animate-spin" />
      ) : isRecording ? (
        <MicOff className="h-5 w-5" />
      ) : (
        <Mic className="h-5 w-5" />
      )}
    </Button>
  );
};
