package com.example.dashcamfrontend;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;

import android.content.pm.PackageManager;
import android.os.Bundle;

public class MainActivity extends AppCompatActivity {

    private boolean cameraPermission;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        getCameraPermission();

        if (!cameraPermission) {
            // Explain that app won't work without the permission.
        }

    }

    private final ActivityResultLauncher<String> requestPermissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestPermission(), isGranted -> {
                if (isGranted) {
                    cameraPermission = true;
                } else {
                    cameraPermission = false;
                }
            });
    private void getCameraPermission(){
        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED) {
            cameraPermission = true;
        } else {
            // Ask for permission
            requestPermissionLauncher.launch(android.Manifest.permission.CAMERA);
        }
    }
}