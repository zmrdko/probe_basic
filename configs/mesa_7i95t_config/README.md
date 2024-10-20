# LinuxCNC 2.9 config for gantry router XYYZ

## Hardware used:
 - MESA 7i95t board
 - Delta ASD-B2-0421-B servo (4pcs)
 - Pilz Pnoz S4 Safety relay
 - LJ12A3-4-Z/AY proximity switch (PNP NC 4mm 6-36VDC)
 - 2.2kW spindle by GPENNY
 - Delta VFD-E

## Features:
 - dual Y gantry
 - on screen safety relay reset
 - precision index homing on all axes


<table>
<tr>
  <td>TB1</td>
  <td>HW pin</td>
  <td>HW connection</td>
  <td>LINUXCNC HAL pin</td>
</tr>
<tr>
  <td rowspan="8">ENCODER5</td>
  <td>/IDX5</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>IDX5</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>+5V</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>/QB5</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>QB5</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>GND</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>/QA5</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>QA5</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td rowspan="8">ENCODER4</td>
  <td>/IDX4</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>IDX4</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>+5V</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>/QB4</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>QB4</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>GND</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>/QA4</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>QA4</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td rowspan="8">ENCODER3</td>
  <td>/IDX3</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>IDX3</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>+5V</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>/QB3</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>QB3</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>GND</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>/QA3</td>
  <td></td>
  <td></td>
</tr>
</tr>
<tr>
  <td>QA3</td>
  <td></td>
  <td></td>
</tr>
</table>
