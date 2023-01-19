package lululab_ocr_app.lululab_app.image_crop_app;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.image_crop.image_crop_app.R;
import com.image_crop.image_crop_app.databinding.ActivityIngreBinding;

public class IngreActivity extends AppCompatActivity {
    ActivityIngreBinding binding;
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityIngreBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
        Intent intent = this.getIntent();
        TextView ingre_risk = (TextView) findViewById(R.id.risk_profile);
        if(intent != null){
            String name = intent.getStringExtra("name");
            String purpose = intent.getStringExtra("purpose");
            String risk = intent.getStringExtra("risk");
            binding.nameProfile.setText(name);
            binding.purposeProfile.setText(purpose);
            binding.riskProfile.setText(risk);

            if(risk.equals("높은 위험도")==true){
                ingre_risk.setTextColor(Color.rgb(228,61,48));
            }else if(risk.equals("중간 위험도")==true){
                ingre_risk.setTextColor(Color.rgb(255,158,24));
            }else if(risk.equals("낮은 위험도")==true){
                ingre_risk.setTextColor(Color.rgb(0,157,79));
            }
        }
    }
}
