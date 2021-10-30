//THIS IS A FIX OF THE ONE BY FRANCY FROG
//THEY FIXED THEIRS
import javax.swing.JFrame;
import javax.swing.*;
import java.awt.BorderLayout;
import java.awt.*;
import java.util.*;

public class MockMinecraftInstance {


    public static class MyJFrame extends JFrame implements Observer {
        private static class MyObservable extends Observable {
            @Override
            public void setChanged() {
                super.setChanged();
            }
        }

        public void update(Observable obs, Object obj) {}
        private final MyObservable observable = new MyObservable();

        @Override
        public void paint(Graphics g) 
        {
            super.paint(g);

            if (Math.random() < 0.1) {

                g.setColor(Color.GREEN);
                g.fillOval(150, -20, 160, 90);
            }
        }
    } 

    public static void main(String[] args){

        int instance = Integer.parseInt(args[0]);

        JFrame frame = new MyJFrame();
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setTitle("Instance " + instance);
        frame.setLayout(new BorderLayout());

        int spacing = 3;
        if (instance >= 10) {

            spacing--;
        }
        if (instance >= 100) {

            spacing--;
        }
        String labelText = "";
        for(int i = 0; i < spacing; i++) {

            labelText += " ";
        }
        labelText += ""+instance;
        for(int i = 0; i < spacing; i++) {

            labelText += " ";
        }
        JLabel label = new JLabel(labelText);
        label.setFont(new Font("Serif", Font.PLAIN, 100));
        frame.add(label, BorderLayout.CENTER);
        
        frame.pack();
        
        frame.setSize(320,180);
        frame.setVisible(true);
        // frame.repaint();
    }
}