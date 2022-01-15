//THIS IS A FIX OF THE ONE BY FRANCY FROG
//THEY FIXED THEIRS
import javax.swing.JFrame;
import javax.swing.*;
import java.awt.BorderLayout;
import java.awt.*;
import java.util.*;
import java.awt.event.*;
import javax.swing.JComponent;

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

    public static class MyAction extends AbstractAction {

        int direction;
        int player;

        public MyAction() {
        }

        @Override
        public void actionPerformed(ActionEvent e) {

            // Same as the move method in the question code.
            // Player can be detected by e.getSource() instead and call its own move method.
            System.out.println("i did the action");
        }
    }

    public static void main(String[] args){

        int instance = Integer.parseInt(args[0]);

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
        JLabel label = new JLabel(labelText);
        label.setFont(new Font("Serif", Font.PLAIN, 100));

        label.setFocusTraversalKeys(KeyboardFocusManager.FORWARD_TRAVERSAL_KEYS, null);
        label.setFocusTraversalKeys(KeyboardFocusManager.BACKWARD_TRAVERSAL_KEYS, null);
        label.setFocusTraversalKeys(KeyboardFocusManager.UP_CYCLE_TRAVERSAL_KEYS, null);

        // label.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke(KeyEvent.getKeyText(KeyEvent.VK_TAB)), "myAction");
        label.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(KeyStroke.getKeyStroke("ENTER"), "myAction");
        label.getActionMap().put("myAction", new MyAction());

        frame.add(label, BorderLayout.CENTER);

        System.out.println(label.getInputMap());
        System.out.println(label.getActionMap());
        
        frame.pack();
        
        frame.setSize(320,180);
        frame.setVisible(true);
        // frame.repaint();
    }
}