import javax.swing.JFrame;
import javax.swing.*;
import java.awt.BorderLayout;
import java.awt.*;
import java.util.*;
import java.awt.event.*;
import javax.swing.JComponent;
import java.io.*;
import java.nio.file.*;

public class MockMinecraftInstance {

    public static final String LOG_DIR = System.getProperty("user.home") + "/.aimlog/";

    private static void assureMyFile() {

        try {

            File myFile = new File(LOG_DIR + instance + ".log");

            if (!myFile.exists()) {

                myFile.createNewFile();
            }
        } catch (IOException ex) {}
    }


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

    public static class MyAction extends AbstractAction {

        int direction;
        int player;

        public MyAction() {
        }

        @Override
        public void actionPerformed(ActionEvent e) {

            MyLogger.onEnterReceived();
        }
    }

    public static class MyKeyListener implements KeyListener {

        public MyKeyListener() {

        }

        public void keyPressed(KeyEvent e) {

            if(e.getKeyCode() == KeyEvent.VK_TAB) {

                MyLogger.onTabReceived();
            }
            if (e.getKeyCode() == KeyEvent.VK_SHIFT) {

                MyLogger.onShiftDownReceived();
            }
            if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {

                MyLogger.onEscReceived();
            }
            if (e.getKeyCode() == KeyEvent.VK_F3) {

                MyLogger.onF3Received();
            }
        }

        public void keyReleased(KeyEvent e) {

            if (e.getKeyCode() == KeyEvent.VK_SHIFT) {

                MyLogger.onShiftUpReceived();
            }
        }

        public void keyTyped(KeyEvent e) {}
    }

    public static class MyLogger {

        private static void writeOut(String text) {

            assureMyFile();

            try {

                FileWriter myWriter = new FileWriter(LOG_DIR + instance + ".log", true);
                BufferedWriter buffWriter = new BufferedWriter(myWriter);
                buffWriter.append(""+System.currentTimeMillis());
                buffWriter.append(" ");
                buffWriter.append(text);
                buffWriter.newLine();
                buffWriter.close();
            } catch (IOException ex) {}
        }

        public static void onTabReceived() {

            writeOut("tab action");
        }

        public static void onEnterReceived() {

            writeOut("enter action");
        }

        public static void onShiftDownReceived() {

            writeOut("shift down action");
        }

        public static void onShiftUpReceived() {

            writeOut("shift up action");
        }

        public static void onEscReceived() {

            writeOut("escape action");
        }

        public static void onF3Received() {

            writeOut("f3 action");
        }
    }

    public static int instance = -1;

    public static void main(String[] args){

        instance = Integer.parseInt(args[0]);

        JFrame frame = new MyJFrame();
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setTitle("Minecraft* - Instance " + instance);
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

        JPanel panel = new JPanel();

        JLabel label = new JLabel(labelText);
        label.setFont(new Font("Serif", Font.PLAIN, 100));

        // label.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.getKeyText(KeyEvent.VK_TAB)), "myAction");
        label.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke("ENTER"), "myAction");
        label.getActionMap().put("myAction", new MyAction());

        JTextField jtf1 = new JTextField(" ");

        jtf1.setFocusTraversalKeysEnabled(false);

        jtf1.addKeyListener(new MyKeyListener());

        panel.add(jtf1);

        frame.add(label, BorderLayout.CENTER);

        frame.add(panel);

        System.out.println(label.getInputMap());
        System.out.println(label.getActionMap());
        
        frame.pack();
        
        frame.setSize(320,180);
        frame.setVisible(true);
    }
}