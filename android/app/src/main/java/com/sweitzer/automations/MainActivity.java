package com.sweitzer.automations;

import android.annotation.SuppressLint;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.webkit.WebViewAssetLoader;

/**
 * Bundled Revenue Pulse + Flip tracker (revenue_pulse/) in assets.
 * WebViewAssetLoader serves them under https://appassets.androidplatform.net/… so fetch() works for sample CSVs.
 */
public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private WebViewAssetLoader assetLoader;

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

    @Override
    @Deprecated
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
