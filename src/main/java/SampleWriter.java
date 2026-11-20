import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;

public class SampleWriter
{
    public static void main(String[] args) throws IOException
    {
        new File("du_lieu_mau").mkdirs();

        write("du_lieu_mau/mau_ngau_nhien_10000.txt", "random");
        write("du_lieu_mau/mau_gan_sap_xep_10000.txt", "nearly");
        write("du_lieu_mau/mau_nguoc_thu_tu_10000.txt", "reversed");
        write("du_lieu_mau/mau_da_sap_xep_10000.txt", "sorted");
    }

    private static void write(String path, String type) throws IOException
    {
        Integer[] a = DataGenerator.generate(type, 10_000, DataGenerator.SEED + 1);
        try (PrintWriter out = new PrintWriter(path))
        {
            for (Integer x : a)
            {
                out.println(x);
            }
        }
        System.out.println("Da tao " + path);
    }
}
