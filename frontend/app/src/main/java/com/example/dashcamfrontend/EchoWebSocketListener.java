package com.example.dashcamfrontend;

import android.graphics.RectF;
import android.util.JsonReader;
import android.util.Log;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import okhttp3.Response;
import okhttp3.WebSocketListener;

public class EchoWebSocketListener extends WebSocketListener {

    private DetectionOverlay detectionOverlay;

    public EchoWebSocketListener(DetectionOverlay detectionOverlay) {
        this.detectionOverlay = detectionOverlay;
    }

    @Override
    public void onOpen(okhttp3.WebSocket webSocket, Response response) {

    }

    @Override
    public void onMessage(okhttp3.WebSocket webSocket, String text) {
        detectionOverlay.post(() -> detectionOverlay.parseResponse(text));
    }

    @Override
    public void onClosing(okhttp3.WebSocket webSocket, int code, String reason) {
        webSocket.close(1000, null);
        Log.i("Closing: ", reason);
    }

    @Override
    public void onFailure(okhttp3.WebSocket webSocket, Throwable t, Response response) {
        t.printStackTrace();
    }

}
