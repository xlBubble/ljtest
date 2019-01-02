
package demo;
 
import java.util.Scanner;

public class demo {
	public static void main(String[] args) {
		
    int a = 10;
    int b = 43;
    int c = 24;
    
		if(a > b){
			if ( b > c) {
				System.out.println("排序后的值为：" + c + "," + b + "," + a);
			}else if( c > a){
				System.out.println("排序后的值为：" + b + ","  + a + "," + c);
			}else{
				System.out.println("排序后的值为：" + b + "," + a + ","  + c);
			}
		}else{
			if(c < a){
                System.out.println("排序后的值为：" + c + "," + a + "," + b);
            }else if(c > b){
                System.out.println("排序后的值为：" + a + "," + b + "," + c);
            }else{
                System.out.println("排序后的值为："+ a + "," + c + "," + b);
            }
		}
	}
