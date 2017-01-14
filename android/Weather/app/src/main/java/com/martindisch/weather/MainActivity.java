package com.martindisch.weather;

import android.graphics.Color;
import android.os.Bundle;
import android.support.v4.content.ContextCompat;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.app.AppCompatActivity;
import android.widget.TextView;
import android.widget.Toast;

import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.components.AxisBase;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.formatter.IAxisValueFormatter;
import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import java.io.IOException;
import java.util.ArrayList;

import cz.msebera.android.httpclient.Header;

public class MainActivity extends AppCompatActivity {

    private TextView mLatestTemp, mLatestHum;
    private SwipeRefreshLayout mSwipeContainer;
    private LineChart mChart;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mLatestTemp = (TextView) findViewById(R.id.tvLatestTemp);
        mLatestHum = (TextView) findViewById(R.id.tvLatestHum);
        mSwipeContainer = (SwipeRefreshLayout) findViewById(R.id.swipeContainer);
        mChart = (LineChart) findViewById(R.id.chart);

        mChart.setDescription(null);
        mChart.setScaleYEnabled(false);
        mChart.setHighlightPerDragEnabled(false);
        mChart.setHighlightPerTapEnabled(false);
        mChart.getLegend().setDrawInside(true);
        mChart.setExtraTopOffset(10);
        XAxis xAxis = mChart.getXAxis();
        xAxis.setLabelRotationAngle(-90);
        xAxis.setLabelCount(10);

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
                            final ArrayList<String[]> history = Util.parseHistory(responseBody);
                            final String[] latest = history.get(history.size() - 1);
                            ArrayList<Entry> temperature = new ArrayList<>(history.size());
                            ArrayList<Entry> humidity = new ArrayList<>(history.size());

                            float counter = 0;
                            for (String[] current : history) {
                                temperature.add(new Entry(counter++, Float.parseFloat(current[1])));
                                humidity.add(new Entry(counter, Float.parseFloat(current[2])));
                            }

                            LineDataSet tempSet = new LineDataSet(temperature, getString(R.string.temperature));
                            tempSet.setDrawCircles(false);
                            tempSet.setColor(Color.RED);
                            LineDataSet humSet = new LineDataSet(humidity, getString(R.string.humidity));
                            humSet.setDrawCircles(false);
                            humSet.setColor(Color.BLUE);

                            final LineData lineData = new LineData(tempSet, humSet);
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    mLatestTemp.setText(String.format(getString(R.string.format_temp), latest[1]));
                                    mLatestHum.setText(String.format(getString(R.string.format_hum), latest[2]));

                                    IAxisValueFormatter formatter = new IAxisValueFormatter() {
                                        @Override
                                        public String getFormattedValue(float value, AxisBase axis) {
                                            return Util.shortenTime(history.get((int) value)[0]);
                                        }
                                    };
                                    mChart.getXAxis().setValueFormatter(formatter);
                                    mChart.setData(lineData);
                                    mChart.invalidate();
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
