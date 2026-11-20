
import java.util.Random;

public class DataGenerator {

    public static final long SEED = 12345L;

    public static Integer[] generate(
            String type, int n, long seed
    ) {
        if (n < 0) {
            throw new IllegalArgumentException(
                    "n phai lon hon hoac bang 0"
            );
        }

        switch (type.toLowerCase()) {

            case "random":
                return random(n, seed);

            case "sorted":
                return sorted(n);

            case "nearly":
                return nearlySorted(n, seed);

            case "reversed":
                return reversed(n);

            default:
                throw new IllegalArgumentException(
                        "Loai du lieu khong hop le: " + type
                );
        }
    }

    // Du lieu ngau nhien
    public static Integer[] random(int n, long seed) {

        Random rnd = new Random(seed);
        Integer[] a = new Integer[n];

        for (int i = 0; i < n; i++) {
            a[i] = rnd.nextInt();
        }

        return a;
    }

    // Du lieu tang dan
    public static Integer[] sorted(int n) {

        Integer[] a = new Integer[n];

        for (int i = 0; i < n; i++) {
            a[i] = i;
        }

        return a;
    }

    // Du lieu gan sap xep
    public static Integer[] nearlySorted(
            int n, long seed
    ) {
        Random rnd = new Random(seed);
        Integer[] a = sorted(n);

        int swaps = n / 100;

        for (int k = 0; k < swaps; k++) {

            int i = rnd.nextInt(n);
            int j = rnd.nextInt(n);

            Integer temp = a[i];
            a[i] = a[j];
            a[j] = temp;
        }

        return a;
    }

    // Du lieu giam dan
    public static Integer[] reversed(int n) {

        Integer[] a = new Integer[n];

        for (int i = 0; i < n; i++) {
            a[i] = n - i;
        }

        return a;
    }
}
