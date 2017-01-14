package com.martindisch.weather;

import android.os.Bundle;
import android.support.v4.content.ContextCompat;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.app.AppCompatActivity;
import android.widget.TextView;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import java.io.IOException;
import java.util.ArrayList;

import cz.msebera.android.httpclient.Header;

public class MainActivity extends AppCompatActivity {

    private TextView mLatestTemp, mLatestHum, mHistory;
    private SwipeRefreshLayout mSwipeContainer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mLatestTemp = (TextView) findViewById(R.id.tvLatestTemp);
        mLatestHum = (TextView) findViewById(R.id.tvLatestHum);
        mHistory = (TextView) findViewById(R.id.tvHistory);
        mSwipeContainer = (SwipeRefreshLayout) findViewById(R.id.swipeContainer);

        mSwipeContainer.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                fetchData();
            }
        });
        mSwipeContainer.setColorSchemeColors(ContextCompat.getColor(this, R.color.colorAccent));

        fetchData();
    }

    private void fetchData() {
        mSwipeContainer.setRefreshing(true);
        AsyncHttpClient client = new AsyncHttpClient();
        client.setMaxRetriesAndTimeout(1, 500);
        client.get("http://" + getString(R.string.IP) + "/history", new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, final byte[] responseBody) {

                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            ArrayList<String[]> history = Util.parseHistory(responseBody);
                            final String[] latest = history.get(history.size() - 1);
                            String history_out = "";
                            for (String[] current : history) {
                                history_out += current[0] + ":" + String.format(getString(R.string.format_both), current[1], current[2]) + "\n";
                            }
                            final String h = history_out;
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    mLatestTemp.setText(String.format(getString(R.string.format_temp), latest[1]));
                                    mLatestHum.setText(String.format(getString(R.string.format_hum), latest[2]));
                                    mHistory.setText(h);
                                }
                            });
                        } catch (IOException e) {
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    Toast.makeText(getApplicationContext(), getString(R.string.error_parsing), Toast.LENGTH_SHORT).show();
                                }
                            });
                        } finally {
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    mSwipeContainer.setRefreshing(false);
                                }
                            });
                        }
                    }
                }).start();
            }

            @Override
            public void onFailure(int statusCode, Header[] headers, byte[] responseBody, Throwable error) {
                Toast.makeText(getApplicationContext(), getString(R.string.error_connecting), Toast.LENGTH_SHORT).show();
                mSwipeContainer.setRefreshing(false);
            }
        });
    }
}
