package com.sweitzer.automations;

import android.annotation.SuppressLint;
import android.content.ActivityNotFoundException;
import android.content.ClipData;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.webkit.WebViewAssetLoader;

/**
 * Bundled Revenue Pulse, Flip tracker, and video player (revenue_pulse/) in assets.
 * WebViewAssetLoader serves them under https://appassets.androidplatform.net/… so fetch() works for sample CSVs.
 */
public class MainActivity extends AppCompatActivity {

    private static final int VIDEO_FILE_CHOOSER_REQUEST = 4701;

    private WebView webView;
    private WebViewAssetLoader assetLoader;
    private ValueCallback<Uri[]> filePathCallback;
    private View fullscreenView;
    private WebChromeClient.CustomViewCallback fullscreenCallback;

    @NonNull
    private WebViewAssetLoader getAssetLoader() {
        if (assetLoader == null) {
            assetLoader =
                    new WebViewAssetLoader.Builder()
                            .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                            .build();
        }
        return assetLoader;
    }

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setAllowFileAccess(true);
        webView.getSettings().setMediaPlaybackRequiresUserGesture(false);
        webView.setWebChromeClient(
                new WebChromeClient() {
                    @Override
                    public boolean onShowFileChooser(
                            WebView webView,
                            ValueCallback<Uri[]> filePathCallback,
                            FileChooserParams fileChooserParams) {
                        if (MainActivity.this.filePathCallback != null) {
                            MainActivity.this.filePathCallback.onReceiveValue(null);
                        }
                        MainActivity.this.filePathCallback = filePathCallback;

                        Intent intent = fileChooserParams.createIntent();
                        intent.setType("video/*");
                        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
                        try {
                            startActivityForResult(intent, VIDEO_FILE_CHOOSER_REQUEST);
                            return true;
                        } catch (ActivityNotFoundException e) {
                            MainActivity.this.filePathCallback = null;
                            filePathCallback.onReceiveValue(null);
                            return false;
                        }
                    }

                    @Override
                    public void onShowCustomView(View view, CustomViewCallback callback) {
                        if (fullscreenView != null) {
                            callback.onCustomViewHidden();
                            return;
                        }
                        fullscreenView = view;
                        fullscreenCallback = callback;
                        webView.setVisibility(View.GONE);
                        addContentView(
                                fullscreenView,
                                new FrameLayout.LayoutParams(
                                        ViewGroup.LayoutParams.MATCH_PARENT,
                                        ViewGroup.LayoutParams.MATCH_PARENT));
                    }

                    @Override
                    public void onHideCustomView() {
                        hideFullscreenView();
                    }
                });
        webView.setWebViewClient(
                new WebViewClient() {
                    @Override
                    public WebResourceResponse shouldInterceptRequest(
                            WebView view, WebResourceRequest request) {
                        Uri url = request.getUrl();
                        return getAssetLoader().shouldInterceptRequest(url);
                    }
                });
        webView.loadUrl("https://appassets.androidplatform.net/assets/revenue_pulse/index.html");
    }

    private void hideFullscreenView() {
        if (fullscreenView == null) {
            return;
        }
        ViewGroup parent = (ViewGroup) fullscreenView.getParent();
        if (parent != null) {
            parent.removeView(fullscreenView);
        }
        fullscreenView = null;
        webView.setVisibility(View.VISIBLE);
        if (fullscreenCallback != null) {
            fullscreenCallback.onCustomViewHidden();
            fullscreenCallback = null;
        }
    }

    @Override
    @Deprecated
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        if (requestCode == VIDEO_FILE_CHOOSER_REQUEST) {
            if (filePathCallback == null) {
                return;
            }
            Uri[] results = null;
            if (resultCode == RESULT_OK && data != null) {
                ClipData clipData = data.getClipData();
                if (clipData != null) {
                    results = new Uri[clipData.getItemCount()];
                    for (int i = 0; i < clipData.getItemCount(); i++) {
                        results[i] = clipData.getItemAt(i).getUri();
                    }
                } else if (data.getData() != null) {
                    results = new Uri[] {data.getData()};
                } else {
                    results = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
                }
            }
            filePathCallback.onReceiveValue(results);
            filePathCallback = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    @Deprecated
    public void onBackPressed() {
        if (fullscreenView != null) {
            hideFullscreenView();
        } else if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
