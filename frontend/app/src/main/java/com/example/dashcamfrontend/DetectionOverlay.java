package com.example.dashcamfrontend;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;

import androidx.annotation.Nullable;

public class DetectionOverlay extends View {

    private RectF[] rects;

    public DetectionOverlay(Context context) {
        super(context);
    }

    public DetectionOverlay(Context context, @Nullable AttributeSet attrs) {
        super(context, attrs);
    }

    public DetectionOverlay(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
    }

    public DetectionOverlay(Context context, @Nullable AttributeSet attrs, int defStyleAttr, int defStyleRes) {
        super(context, attrs, defStyleAttr, defStyleRes);
    }

    /**
     *
     * Sets the private variable rectangles, and invalidates the view
     * so onDraw is called.
     * @param rects Array of rectangles to be drawn
     */
    public void setRect(RectF[] rects) {

    }

    /**
     * Automatically called after view is invalidated.
     * Iterates over rects array and draws them on canvas.
     *
     * @param canvas The canvas of the view that we draw the rects on
     */
    @Override
    protected void onDraw(Canvas canvas) {

    }

}
