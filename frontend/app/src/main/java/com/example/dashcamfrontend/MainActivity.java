package com.example.dashcamfrontend;

import static androidx.camera.core.AspectRatio.RATIO_16_9;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.annotation.OptIn;
import androidx.annotation.Size;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.AspectRatio;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ExperimentalGetImage;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.ImageProxy;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.LifecycleOwner;

import android.app.Dialog;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.google.common.util.concurrent.ListenableFuture;

import java.io.ByteArrayOutputStream;
import java.util.concurrent.ExecutionException;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.WebSocket;
import okio.ByteString;
import utils.BitmapUtils;

public class MainActivity extends AppCompatActivity {

    private PreviewView previewView;
    private boolean cameraPermission;
    private ListenableFuture<ProcessCameraProvider> cameraProviderFuture;
    private WebSocket webSocket;
    private DetectionOverlay detectionOverlay;
    private long time;
    private EchoWebSocketListener listener;

    private float aspectRatio = -1f;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        previewView = findViewById(R.id.previewView);
        detectionOverlay = findViewById(R.id.overlayView);

        getCameraPermission();

        if (!cameraPermission) {
            // Explain that app won't work without the permission.
        }

        showWebSocketPopup();

    }

    private final ActivityResultLauncher<String> requestPermissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestPermission(), isGranted -> {
                cameraPermission = isGranted;
            });

    private void setupWebsocket(String ipAddress) {
        time = System.currentTimeMillis();

        // Set up websocket
        OkHttpClient client = new OkHttpClient();
        String websocketUrl = "ws://" + ipAddress + ":8001"; // insert ipv4 address + port here
        Request request = new Request.Builder().url(websocketUrl).build();

        listener = new EchoWebSocketListener(detectionOverlay);
        webSocket = client.newWebSocket(request, listener);


        // Follows camerax docs - preview use case
        cameraProviderFuture = ProcessCameraProvider.getInstance(this);

        cameraProviderFuture.addListener(() -> {
            try {
                ProcessCameraProvider cameraProvider = cameraProviderFuture.get();
                bindPreview(cameraProvider);
            } catch (ExecutionException | InterruptedException e) {
                // No errors need to be handled for this Future.
                // This should never be reached.
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void getCameraPermission(){
        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED) {
            cameraPermission = true;
        } else {
            // Ask for permission
            requestPermissionLauncher.launch(android.Manifest.permission.CAMERA);
        }
    }

    private void showWebSocketPopup() {
        // Create dialog
        Dialog dialog = new Dialog(this);
        dialog.setContentView(R.layout.popup_layout);

        // Get views from dialog layout
        EditText editTextWebSocketAddress = dialog.findViewById(R.id.editTextWebSocketAddress);
        Button buttonConnectWebSocket = dialog.findViewById(R.id.buttonConnectWebSocket);

        // Set click listener for button
        buttonConnectWebSocket.setOnClickListener(view -> {
            String ip = editTextWebSocketAddress.getText().toString().trim();
            if (!ip.isEmpty()) {
                // Set up WebSocket
                setupWebsocket(ip);
                dialog.dismiss();
            } else {
                Toast.makeText(this, "Please enter a valid WebSocket IP address", Toast.LENGTH_SHORT).show();
            }
        });

        dialog.show();
    }

    void bindPreview(@NonNull ProcessCameraProvider cameraProvider) {
        Preview preview = new Preview.Builder()
                .build();
        CameraSelector cameraSelector = new CameraSelector.Builder()
                .requireLensFacing(CameraSelector.LENS_FACING_BACK)
                .build();
        preview.setSurfaceProvider(previewView.getSurfaceProvider());

        // Follows camerax docs - image analysis use case
        ImageAnalysis imageAnalysis =
                new ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build();
        imageAnalysis.setAnalyzer(AsyncTask.THREAD_POOL_EXECUTOR, new ImageAnalysis.Analyzer() {
            @Override
            @OptIn(markerClass = ExperimentalGetImage.class)
            public void analyze(@NonNull ImageProxy imageProxy) { // called for every new frame
                // Uses Googles BitmapUtils to convert image proxy to bitmap
                Bitmap bitmap = BitmapUtils.getBitmap(imageProxy);
                imageProxy.close();
                if (aspectRatio < 0) {
                    // Calculate the aspect ratio if it hasn't been calculated before
                    int imageWidth = imageProxy.getWidth();
                    int imageHeight = imageProxy.getHeight();
                    detectionOverlay.setAspectRatio(imageWidth, imageHeight);
                }
                // Compress bitmap to JPEG
                ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
                if(bitmap != null) {
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 80, byteArrayOutputStream);
                }
                byte[] byteArray = byteArrayOutputStream.toByteArray();
                // Send ByteString of image to backend
                if (System.currentTimeMillis() - time > 600) { // set delay to not overcrowd backend
                    time = System.currentTimeMillis(); // update time
                    webSocket.send(ByteString.of(byteArray));
                }
            }
        });
        // bind image analysis
        cameraProvider.bindToLifecycle(this, cameraSelector, imageAnalysis, preview);
    }
}