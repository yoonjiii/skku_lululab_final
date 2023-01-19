package lululab_ocr_app.lululab_app.image_crop_app;

import androidx.activity.result.ActivityResult;
import androidx.activity.result.ActivityResultCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.IdRes;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.provider.Settings;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import com.image_crop.image_crop_app.R;
import com.image_crop.image_crop_app.databinding.ActivityMainBinding;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Objects;


public class MainActivity extends AppCompatActivity {

    private static final int MY_PERMISSION_CAMERA = 1111;

    private ActivityResultLauncher<Intent> resultLauncher;

    Button btn_capture, btn_album, btn_result;
    ImageView iv_view;
    TextView txt;
    ListView list;
    String mCurrentPhotoPath;
    Uri photoURI;
    Uri contentUri;
    JSONObject jsonObject = new JSONObject();
    int lan = 0;
    int option = 0;
    private RadioGroup radioGroup1;
    private RadioGroup radioGroup2;

    ActivityMainBinding binding;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        btn_capture = (Button) findViewById(R.id.btn_capture);
        btn_album = (Button) findViewById(R.id.btn_album);
        btn_result = (Button) findViewById(R.id.btn_result);
        iv_view = (ImageView) findViewById(R.id.iv_view);
        txt = (TextView) findViewById(R.id.textView);
        list = (ListView) findViewById(R.id.list);
        radioGroup1 = (RadioGroup) findViewById(R.id.radio_lan);
        radioGroup1.setOnCheckedChangeListener(radioGroupButtonChangeListener1);
        radioGroup2 = (RadioGroup) findViewById(R.id.radio_option);
        radioGroup2.setOnCheckedChangeListener(radioGroupButtonChangeListener2);

        btn_capture.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                captureCamera();
            }
        });

        btn_album.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getAlbum();
            }
        });

        btn_result.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                getResult();
            }
        });
        checkPermission();
    }

    RadioGroup.OnCheckedChangeListener radioGroupButtonChangeListener1 = new RadioGroup.OnCheckedChangeListener() {
        @Override
        public void onCheckedChanged(RadioGroup radioGroup, @IdRes int i) {
            if(i == R.id.radio_lan_eng){
                lan = 1;
            }
            else if(i == R.id.radio_lan_kor){
                lan = 2;
            }
            try{
                jsonObject.put("language", Integer.toString(lan));
                Log.i("json content",jsonObject.toString());
            }catch(Exception e){
                Log.e("CHOOSING LANGUAGE", e.toString());
            }
        }
    };

    RadioGroup.OnCheckedChangeListener radioGroupButtonChangeListener2 = new RadioGroup.OnCheckedChangeListener() {
        @Override
        public void onCheckedChanged(RadioGroup radioGroup, @IdRes int i) {
            if(i == R.id.radio_option_1){
                option = 1;
            }
            else if(i == R.id.radio_option_2){
                option = 2;
            }
            try{
                jsonObject.put("option", Integer.toString(option));
                Log.i("json content",jsonObject.toString());
            }catch(Exception e){
                Log.e("CHOOSING OPTION", e.toString());
            }
        }
    };

    ActivityResultLauncher<Intent> requestSavePhoto = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            new ActivityResultCallback<ActivityResult>() {
                @Override
                public void onActivityResult(ActivityResult result) {
                    if (result.getResultCode()==RESULT_OK) {
                        try {
                            Log.i("REQUEST_TAKE_PHOTO", "OK");
                            galleryAddPic();
                            iv_view.setImageURI(contentUri);
                            EncodingImage(contentUri);
                        } catch (Exception e) {
                            Log.e("REQUEST_TAKE_PHOTO", e.toString());
                        }
                    }
                    else {
                        //cancelled
                        Toast.makeText(MainActivity.this, "사진촬영을 취소했습니다.", Toast.LENGTH_SHORT).show();
                    }
                }
            }
    );

    private void EncodingImage(Uri uri) throws IOException {
        Bitmap bitmapPicture = MediaStore.Images.Media.getBitmap(getContentResolver(),uri);
        final int COMPRESSION_QUALITY = 100;
        String encodedImage;
        ByteArrayOutputStream byteArrayBitmapStream = new ByteArrayOutputStream();
        bitmapPicture.compress(Bitmap.CompressFormat.PNG, COMPRESSION_QUALITY,
                byteArrayBitmapStream);
        byte[] b = byteArrayBitmapStream.toByteArray();
        encodedImage = Base64.encodeToString(b, Base64.DEFAULT);
        try{
            jsonObject.put("image",encodedImage);
            Log.i("json content",jsonObject.toString());
        }catch (JSONException e) {
            e.printStackTrace();
        }
    }

    void getResult(){
        new MyAsyncTask().execute();
    }

    class MyAsyncTask extends AsyncTask<Void, Void, Void> {
        @Override
        protected Void doInBackground(Void... voids) {
            HttpURLConnection con = null;
            try{
                Log.i("sending", "sending image");
                String page = "http://61.98.7.199:17000/";
                URL url = new URL(page);
                con = (HttpURLConnection) url.openConnection();
                con.setRequestMethod("POST");
                con.setRequestProperty("Content-Type", "application/json");
                con.setRequestProperty("Accept", "application/json");
                con.setDoOutput(true);
                BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(con.getOutputStream()));

                bw.write(jsonObject.toString());
                bw.flush();
                bw.close();

                BufferedReader br = new BufferedReader(new InputStreamReader(con.getInputStream()));
                StringBuilder sb = new StringBuilder();
                String line = "";
                while ((line = br.readLine()) != null) {
                    sb.append(line);
                }
                br.close();
                String response = sb.toString();
                Log.i("sb", response);

                showResult(response);

            } catch (Exception e) {
                Log.i("Error occured", "error:" + e);
            }
            return null;
        }
    }

    void showResult(String result){
        if (result.equals("no data")) {
            runOnUiThread(() -> {
                Toast.makeText(this, "데이터가 없는 화장품입니다.\n화장품 성분표로 다시 검색해주세요.", Toast.LENGTH_LONG).show();
            });

        }else {
            int size = 0;
            try{
                JSONArray tmp = new JSONArray(result);
                Log.i("tmp", Integer.toString(tmp.length()));

                size = tmp.length();
                String[] name = new String[size];
                String[] purpose = new String[size];
                String[] risk = new String[size];

                for(int i = 0; i< tmp.length(); i++){
                    JSONObject ob = tmp.getJSONObject(i);
                    name[i] = ob.getString("class");
                    purpose[i] = ob.getString("purpose");
                    risk[i] = "낮은 위험도";
                }

                ArrayList<Ingredients> ingreArrayList = new ArrayList<>();

                for(int i = 0; i< name.length; i++){
                    Ingredients ingre = new Ingredients(name[i],purpose[i],risk[i]);
                    ingreArrayList.add(ingre);
                }

                runOnUiThread(() -> {
                    ListAdapter listAdapter = new ListAdapter(MainActivity.this, ingreArrayList);
                    binding.list.setAdapter(listAdapter);
                    binding.list.setClickable(true);
                    binding.list.setOnItemClickListener(new AdapterView.OnItemClickListener() {
                        @Override
                        public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                            Intent i = new Intent(MainActivity.this, IngreActivity.class);
                            i.putExtra("name", name[position]);
                            i.putExtra("purpose",purpose[position]);
                            i.putExtra("risk", risk[position]);
                            startActivity(i);
                        }
                    });
                });
            }catch(Exception e){
                Log.e("Showing result", e.toString());
            }
        }
    }

    ActivityResultLauncher<Intent> requestTakeAlbum = registerForActivityResult(
            new ActivityResultContracts.StartActivityForResult(),
            new ActivityResultCallback<ActivityResult>() {
                @Override
                public void onActivityResult(ActivityResult result) {
                    if (result.getResultCode() == Activity.RESULT_OK) {
                        Intent intent = result.getData();
                        Uri uri = intent.getData();
                        iv_view.setImageURI(uri);
                        try {
                            EncodingImage(uri);
                        } catch (IOException e) {
                        }
                    }
                }
            }
    );

    private void captureCamera(){
        String state = Environment.getExternalStorageState();
        if(Environment.MEDIA_MOUNTED.equals(state)){
            Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

            if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
                File photoFile = null;
                try {
                    photoFile = createImageFile();
                } catch (IOException ex) {
                    // Error occurred while creating the File
                    Log.e("Error_creating_File", ex.toString());
                }
                if (photoFile != null) {

                    //photoURI = FileProvider.getUriForFile(this, "com.example.local_e", photoFile);
                    photoURI = FileProvider.getUriForFile(Objects.requireNonNull(getApplicationContext()),
                            BuildConfig.APPLICATION_ID + ".provider", photoFile);
                    Log.i("photoFile", photoFile.toString());
                    Log.i("photoURI", photoURI.toString());

                    takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
                    //startActivityForResult(takePictureIntent, REQUEST_TAKE_PHOTO);
                    requestSavePhoto.launch(takePictureIntent);
                }
            }
        } else {
            Toast.makeText(this, "저장공간이 접근 불가능한 기기입니다", Toast.LENGTH_SHORT).show();
            return;
        }
    }

    public File createImageFile() throws IOException {
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "JPEG_" + timeStamp + ".jpg";
        File imageFile = null;
        File storageDir = new File(Environment.getExternalStorageDirectory() + "/DCIM", "Camera");

        if (!storageDir.exists()) {
            Log.i("mCurrentPhotoPath1", storageDir.toString());
            storageDir.mkdirs();
        }

        imageFile = new File(storageDir, imageFileName);
        mCurrentPhotoPath = imageFile.getAbsolutePath();

        return imageFile;
    }


    private void getAlbum(){
        Log.i("getAlbum", "Call");
        Intent intent = new Intent();
        intent.setType("image/*");
        intent.putExtra("crop", true);
        intent.setAction(Intent.ACTION_GET_CONTENT);
        requestTakeAlbum.launch(intent);
    }

    private void galleryAddPic(){
        Log.i("galleryAddPic", "Call");
        Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
        // 해당 경로에 있는 파일을 객체화(새로 파일을 만든다는 것으로 이해하면 안 됨)
        File f = new File(mCurrentPhotoPath);
        contentUri = Uri.fromFile(f);
        mediaScanIntent.setData(contentUri);
        sendBroadcast(mediaScanIntent);
        Toast.makeText(this, "사진이 앨범에 저장되었습니다.", Toast.LENGTH_SHORT).show();

    }

    private void checkPermission(){
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            // 처음 호출시엔 if()안의 부분은 false로 리턴 됨 -> else{..}의 요청으로 넘어감
            if ((ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)) ||
                    (ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA))) {
                new AlertDialog.Builder(this)
                        .setTitle("알림")
                        .setMessage("저장소 권한이 거부되었습니다. 사용을 원하시면 설정에서 해당 권한을 직접 허용하셔야 합니다.")
                        .setNeutralButton("설정", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialogInterface, int i) {
                                Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                                intent.setData(Uri.parse("package:" + getPackageName()));
                                startActivity(intent);
                            }
                        })
                        .setPositiveButton("확인", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialogInterface, int i) {
                                finish();
                            }
                        })
                        .setCancelable(false)
                        .create()
                        .show();
            } else {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE, Manifest.permission.CAMERA}, MY_PERMISSION_CAMERA);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode) {
            case MY_PERMISSION_CAMERA:
                for (int i = 0; i < grantResults.length; i++) {
                    // grantResults[] : 허용된 권한은 0, 거부한 권한은 -1
                    if (grantResults[i] < 0) {
                        Toast.makeText(MainActivity.this, "해당 권한을 활성화 하셔야 합니다.", Toast.LENGTH_SHORT).show();
                        return;
                    }
                }
                break;
        }
    }
}