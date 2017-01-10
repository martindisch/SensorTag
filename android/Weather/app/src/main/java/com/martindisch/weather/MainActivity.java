package com.martindisch.weather;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import org.w3c.dom.Text;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;

import cz.msebera.android.httpclient.Header;

public class MainActivity extends AppCompatActivity {

    private TextView mLatestTemp, mLatestHum, mHistory;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mLatestTemp = (TextView) findViewById(R.id.tvLatestTemp);
        mLatestHum = (TextView) findViewById(R.id.tvLatestHum);
        mHistory = (TextView) findViewById(R.id.tvHistory);

        AsyncHttpClient client = new AsyncHttpClient();
        client.get("http://" + getString(R.string.IP) + "/history", new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, byte[] responseBody) {
                try {
                    ArrayList<String[]> history = Util.parseHistory(responseBody);
                    String[] latest = history.get(history.size() - 1);
                    mLatestTemp.setText(String.format(getString(R.string.format_temp), latest[1]));
                    mLatestHum.setText(String.format(getString(R.string.format_hum), latest[2]));
                    String history_out = "";
                    for (String[] current : history) {
                        history_out += current[0] + ":" + String.format(getString(R.string.format_both), current[1], current[2]) + "\n";
                    }
                    mHistory.setText(history_out);
                } catch (IOException e) {
                    Toast.makeText(getApplicationContext(), getString(R.string.error_parsing), Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(int statusCode, Header[] headers, byte[] responseBody, Throwable error) {
                Toast.makeText(getApplicationContext(), getString(R.string.error_connecting), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
