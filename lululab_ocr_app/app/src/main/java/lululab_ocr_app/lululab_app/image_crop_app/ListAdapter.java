package lululab_ocr_app.lululab_app.image_crop_app;

import android.content.Context;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.image_crop.image_crop_app.R;

import java.util.ArrayList;

public class ListAdapter extends ArrayAdapter<Ingredients> {
    public ListAdapter(Context context, ArrayList<Ingredients> ingreArrayList){
        super(context, R.layout.list_item, ingreArrayList);

    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        Ingredients ingre = getItem(position);
        if(convertView == null){
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.list_item,parent,false);
        }

        TextView ingre_name = convertView.findViewById(R.id.ingre_name);
        TextView ingre_purpose = convertView.findViewById(R.id.ingre_purpose);
        TextView ingre_risk = convertView.findViewById(R.id.ingre_risk);
        ingre_name.setText(ingre.name);
        ingre_purpose.setText(ingre.purpose);
        ingre_risk.setText(ingre.risk);

        if(ingre.risk == "높은 위험도"){
            ingre_risk.setTextColor(Color.rgb(228,61,48));
        }else if(ingre.risk == "중간 위험도"){
            ingre_risk.setTextColor(Color.rgb(255,158,24));
        }else if(ingre.risk == "낮은 위험도"){
            ingre_risk.setTextColor(Color.rgb(0,157,79));
        }

        return convertView;
    }
}
