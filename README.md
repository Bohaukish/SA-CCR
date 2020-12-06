# SACCR

SACCR is a standardised model for measuring counterparty credit risk exposure.

Two components: Replacement Cost(RC) and Potential Future Exposure(PFE)

Counterparty Credit Risk = alpha * (RC + PFE)

(where alpha equals 1.4, which is carried over from the alpha value set by the Basel Committee for the Internal Model Method (IMM).)

## RC

V = the value of the derivative transactions in the netting set , C = the haircut value of the net collateral held.

- For margined transactions, RC = max(V - C, 0), in this case, we use this formula only.

- For unmargined transactions, 

## PFE add-on

PFE add-on = multiplier * add-on

Steps:

1. add-on

  - Supervisory Duration

  - adjusted notional

  - Effective Notional

2. multiplier

   multiplier = min(1;0.05 + 0.95*exp(M to M- collateral/2*0.95*add-on))
