import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Random;

public class Benchmark {
    static final long ORDER_SEED = 20261120L;

    private static final String RUN_ID =
            System.getProperty("runId", "run1");

    static final int[] SIZES = {10_000, 100_000, 1_000_000};
    static final int[] CUTOFFS = {1, 2, 3, 5, 7, 10, 15, 20, 30, 50};
    static final String[] TYPES = {"random", "nearly", "reversed", "sorted"};

    // Số lần lặp theo kích thước
    static final int REPS_SMALL = 40;   // n <= 10_000
    static final int REPS_MEDIUM = 30;   // n <= 100_000
    static final int REPS_LARGE = 10;    // n > 100_000

    static final int DISCARD_REPS = 3;

    static final int WARMUP_N = 200_000;
    static final int WARMUP_ROUNDS = 3;


    public static void main(String[] args) throws IOException {
        String outDir = "ket_qua";

        new File(outDir).mkdirs();

        // Tạo tên file riêng cho mỗi lần chạy JVM
        String outputFile = outDir + "/raw_" + RUN_ID + ".csv";

        try (PrintWriter out = new PrintWriter(outputFile)) {
            out.println("type,n,cutoff,rep,time_ms");

            Random orderRandom = new Random(ORDER_SEED);

            for (String type : TYPES) {
                warmUp(type);

                for (int n : SIZES) {
                    System.gc();

                    for (int d = 0; d < DISCARD_REPS; d++) {
                        Integer[] base = DataGenerator.generate(
                                type, n, DataGenerator.SEED - 1 - d);

                        for (int cutoff : shuffledCutoffs(orderRandom)) {
                            timeSort(base, cutoff);
                        }
                    }

                    int reps = repsFor(n);

                    for (int rep = 1; rep <= reps; rep++) {
                        Integer[] base = DataGenerator.generate(
                                type, n, DataGenerator.SEED + rep);

                        for (int cutoff : shuffledCutoffs(orderRandom)) {
                            long nanos = timeSort(base, cutoff);
                            double timeMs = nanos / 1_000_000.0;

                            out.printf(
                                    Locale.US,
                                    "%s,%d,%d,%d,%.6f%n",
                                    type, n, cutoff, rep, timeMs
                            );
                        }

                        out.flush();
                    }

                    System.out.println(
                            "Xong: " + type + ", n=" + n
                                    + " (" + reps + " lan lap)"
                    );
                }
            }
        }

        System.out.println(
                "Hoan tat. Ket qua nam trong " + outputFile
        );
    }


    private static int repsFor(int n) {
        if (n <= 10_000) {
            return REPS_SMALL;
        }
        if (n <= 100_000) {
            return REPS_MEDIUM;
        }
        return REPS_LARGE;
    }

    // Sắp xếp một bản sao của base với CUTOFF cho trước; trả về thời gian (ns).
    // Việc sao chép và kiểm tra kết quả nằm ngoài khoảng đo.
    private static long timeSort(Integer[] base, int cutoff) {
        Integer[] a = base.clone();
        MergeSort.setCutoff(cutoff);

        long start = System.nanoTime();
        MergeSort.sort(a);
        long end = System.nanoTime();

        if (!MergeSort.isSorted(a)) {
            throw new IllegalStateException(
                    "Sort sai: n=" + a.length + ", cutoff=" + cutoff);
        }
        return end - start;
    }

    private static List<Integer> shuffledCutoffs(Random random) {
        List<Integer> order = new ArrayList<>();
        for (int cutoff : CUTOFFS) {
            order.add(cutoff);
        }
        Collections.shuffle(order, random);
        return order;
    }

    // Warm-up JIT trên đúng dạng dữ liệu sắp được đo.
    private static void warmUp(String type) {
        System.out.println("Dang warm-up JVM cho dang '" + type + "'...");

        Integer[] base = DataGenerator.generate(type, WARMUP_N, DataGenerator.SEED - 100);

        for (int round = 0; round < WARMUP_ROUNDS; round++) {
            for (int cutoff : CUTOFFS) {
                timeSort(base, cutoff);
            }
        }
    }
}