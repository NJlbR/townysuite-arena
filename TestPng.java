
import javax.imageio.ImageIO;
import java.io.File;
import java.awt.image.BufferedImage;

public class TestPng {
    public static void main(String[] args) throws Exception {
        BufferedImage img1 = ImageIO.read(new File("public/models/cannon_wood.png"));
        System.out.println("Wood PNG valid: " + (img1 != null) + ", width=" + img1.getWidth() + ", height=" + img1.getHeight());
        BufferedImage img2 = ImageIO.read(new File("public/models/cannon_metal.png"));
        System.out.println("Metal PNG valid: " + (img2 != null) + ", width=" + img2.getWidth() + ", height=" + img2.getHeight());
    }
}
