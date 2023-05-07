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
            String [] cords = coordinates[i].split(",");
            if(cords.length == 4) {

                int screenHeight = this.getHeight();
                int screenWidth = this.getWidth();

                float realHeight = screenWidth*0.75F;
                float heightDiff = (realHeight - screenHeight) / 2;

                float left = (Float.parseFloat(cords[0])/640)*screenWidth;
                float top = (((Float.parseFloat(cords[1]))/480)*realHeight);
                float right = (Float.parseFloat(cords[2])/640)*screenWidth;
                float bottom = (((Float.parseFloat(cords[3]))/480)*realHeight);

                bottom -= heightDiff;
                top -= heightDiff;

                RectF exampleRectangle2 = new RectF(left, top, right, bottom);
                rectangles[i] = exampleRectangle2;
            }
            setRects(rectangles);
        }
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

}
