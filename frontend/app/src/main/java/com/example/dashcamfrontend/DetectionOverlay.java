package com.example.dashcamfrontend;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;

import androidx.annotation.Nullable;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Arrays;
import java.util.List;

public class DetectionOverlay extends View {

    private RectF[] rects;
    private String[] labels;
    private Paint paint;
    private Paint textPaint;
    private Bitmap[] bitmaps;

    private int imageWidth;
    private int imageHeight;

    private float aspectRatio;

    public DetectionOverlay(Context context) {
        super(context);
    }

    public DetectionOverlay(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
        paint = new Paint();
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(5f);
        paint.setColor(Color.RED);

        bitmaps = new Bitmap[43];
        for (int i = 0; i < 43; i++) { // load all images of traffic signs into buffer
            String imageName = "sign_" + i;
            Resources resources = context.getResources();
            final int resourceId = resources.getIdentifier(imageName, "drawable",
                    context.getPackageName());

            bitmaps[i] = BitmapFactory.decodeResource(getResources(), resourceId);
        }
    }

    public DetectionOverlay(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
    }

    public DetectionOverlay(Context context, @Nullable AttributeSet attrs, int defStyleAttr, int defStyleRes) {
        super(context, attrs, defStyleAttr, defStyleRes);
    }

    /**
     * Saves the cords from the response in the rectangles array and calls setRects.
     *
     * Still needs more comments - calculation is not obvious without them!
     *
     * @param response the response from the backend, containing the bounding box cords
     */
    public void parseResponse(String response) {
        Log.i("response", response);
        ObjectMapper mapper = new ObjectMapper();
        String [][] arrays; // split up response array into bounding box coordinates and labels
        try {
            arrays = mapper.readValue(response, String[][].class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }

        String[] coordinates = arrays[0];
        labels = arrays[1];
        RectF[] rectangles = new RectF[coordinates.length];

        for (int i = 0; i < coordinates.length; i++) {
            // example coordinates array: ["283.0,3.0,311.0,37.0", "248.0,3.0,277.0,37.0"]
            String [] cords = coordinates[i].split(",");
            if(cords.length == 4) {
                float screenHeight = this.getHeight();
                float screenWidth = this.getWidth();
                // adjust height to aspect ratio of frame - otherwise cords are distorted
                float realHeight = screenWidth*this.aspectRatio;
                float heightDiff = (realHeight - screenHeight) / 2;
                // adjust frame coordinates to phone screen
                float left = (Float.parseFloat(cords[0])/this.imageWidth)*screenWidth;
                float top = (Float.parseFloat(cords[1])/this.imageHeight)*realHeight;
                float right = (Float.parseFloat(cords[2])/this.imageWidth)*screenWidth;
                float bottom = (Float.parseFloat(cords[3])/this.imageHeight)*realHeight;
                // cut off excess height
                bottom -= heightDiff;
                top -= heightDiff;

                RectF tempRectangle = new RectF(left, top, right, bottom);
                rectangles[i] = tempRectangle;
            }
        }
        setRects(rectangles); // invalidates view, triggers new onDraw
    }

    /**
     *
     * Sets the private variable rectangles, and invalidates the view
     * so onDraw is called.
     *
     * @param rects Array of rectangles to be drawn
     */
    public void setRects(RectF[] rects) {
        this.rects = rects;
        invalidate();
    }

    /**
     * Automatically called after view is invalidated.
     * Iterates over rects array and draws them on canvas.
     *
     * @param canvas The canvas of the view that we draw the rects on
     */
    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if (rects != null) { // draw all found bounding boxes
            for (RectF rect : rects) {
                if (rect != null) {
                    canvas.drawRect(rect, paint);
                }
            }
            int index = 0;
            for(String label: labels) { // draw image of recognized traffic signs
                Bitmap bitmap = bitmaps[Integer.parseInt(label)];
                canvas.drawBitmap(bitmap, 250*(index++), 100, null);
            }
        }
    }

    public void setAspectRatio(int imageWidth, int imageHeight) {
        this.imageWidth = imageWidth;
        this.imageHeight = imageHeight;
        this.aspectRatio = (float) imageHeight / imageWidth;
    }
}
