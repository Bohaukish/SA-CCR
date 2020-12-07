# SACCR

SACCR is a standardised model for measuring counterparty credit risk exposure.

Two components: Replacement Cost(RC) and Potential Future Exposure(PFE)

Counterparty Credit Risk = alpha * (RC + PFE)

(where alpha equals 1.4, which is carried over from the alpha value set by the Basel Committee for the Internal Model Method (IMM).)

## RC

V = the value of the derivative transactions in the netting set , C = the haircut value of the net collateral held.

- For margined transactions, RC = max(V(MTM) - C(Collateral), 0), in this case, we use margined transactions only.

- For unmargined transactions, 

## PFE add-on

PFE add-on = multiplier * add-on

Steps:

1. add-on

  - Supervisory Duration

  - adjusted notional

  - Effective Notional
  
    时间分桶，当bucket的时间越近，correlation的系数越大

2. multiplier

   multiplier = min(1 ; 0.05 + 0.95 * exp(M to M - collateral/ 2 * 0.95 * add-on))
   
   delta那个公式用来干嘛的？？？
      
Dataset Description:
   

