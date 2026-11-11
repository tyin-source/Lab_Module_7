// Phys 39 Module 7 - six-thermistor rod acquisition with TEC control (Arduino side)
// (copied from the Module 6 sketch, arduino/module6_pi_control/module6_pi_control.ino
// in the Module 6 repository, which stays unchanged as the working checkpoint)
//
// Changes from Module 6:
//   - Six thermistor channels: A0 = TEC-base thermistor, A1-A5 = rod thermistors
//     T1-T5. All six use the same conversion, adcToTemperatureC(), each with the
//     measured value of its own divider resistor (SERIES_RESISTOR_OHM below).
//   - The TEC-base thermistor (A0) alone is used for the software temperature
//     limit. The rod thermistors are measurement channels only. (The P/PI
//     feedback law is calculated in Python, as in Module 6, from the TEC value.)
//   - Each acquisition cycle prints exactly one comma-separated DATA record:
//       DATA,time_s,tec_C,rod1_C,rod2_C,rod3_C,rod4_C,rod5_C,pwm,heat_cool,setpoint_C,safety
//     The first DATA line, printed once at startup, is the header above.
//     Status, safety, and error messages never begin with DATA.
//   - New command SETPOINT <value in C> | SETPOINT OFF. The Arduino only stores
//     the value and echoes it in the setpoint_C field, so the serial record (and
//     the microSD logger in Module 8) shows the setpoint the Python controller is
//     using. It does not change the PWM and does not reset the command timeout.
//   - Each channel is read twice after the multiplexer switches to it and only the
//     second reading is kept: the 100 kOhm dividers are high-impedance sources, and
//     the first reading after a switch can still carry part of the previous channel.
//
// Pin 9 / Pin 10: H-bridge control signals (unchanged)
//
// Commands from the Python GUI:
//   SET PWM 120 DIR HEAT
//   SET PWM 45 DIR COOL
//   SETPOINT 45.00
//   SETPOINT OFF
//
// heat_cool = 1 only for observed HEATING, 0 only for observed COOLING.
// safety = OK, or SHUTDOWN while the software temperature limit holds both
// H-bridge PWM outputs at zero.
// The Arduino itself is open-loop: it applies whatever PWM and direction the last
// command asked for. Python closes the loop.

// ------------------------------------------------------------------
// CHANNELS
// ------------------------------------------------------------------
const int NUM_CHANNELS = 6;
// Index 0 is the TEC-base thermistor; indices 1-5 are rod thermistors T1-T5.
const int THERMISTOR_PINS[NUM_CHANNELS] = {A0, A1, A2, A3, A4, A5};
const int TEC_CHANNEL = 0;

const int HBRIDGE_PIN_1 = 9;
const int HBRIDGE_PIN_2 = 10;

// Measurement sequence: every SAMPLE_INTERVAL_US, read all six channels once
// (each twice, keeping the second reading). After ADC_SAMPLES such readings, each
// channel's temperature is calculated from its average and one DATA record is
// printed. 500 x 2000 us gives about one record per second, as in Module 6.
// Twelve analogRead() calls take about 1.4 ms, inside the 2 ms interval.
const int ADC_SAMPLES = 500;
const unsigned long SAMPLE_INTERVAL_US = 2000;

// Thermistor constants -- Module 2 values. adcToTemperatureC() assumes the
// Module 3 divider arrangement: external resistor from 5 V to the analog input,
// thermistor from the analog input to GND.
// SERIES_RESISTOR_OHM: replace each 100000.0 with the resistance of that
// channel's divider resistor measured with the meter in Phase 1, and record the
// same values in the sensor map.
const float SERIES_RESISTOR_OHM[NUM_CHANNELS] = {
  100000.0,  // A0  TEC
  100000.0,  // A1  T1 (rod, x = 0, first hole)
  100000.0,  // A2  T2
  100000.0,  // A3  T3
  100000.0,  // A4  T4
  100000.0   // A5  T5
};
const float NOMINAL_RESISTANCE = 100000.0;
const float NOMINAL_TEMPERATURE_C = 25.0;
const float BETA_COEFFICIENT = 4540.0;
const float ADC_MAX = 1023.0;

// ------------------------------------------------------------------
// SOFTWARE TEMPERATURE LIMIT (TEC-base thermistor only)
// ------------------------------------------------------------------
// If the averaged TEC temperature is above this limit, or the TEC channel has no
// valid reading, both H-bridge PWM outputs are set to zero. A missing rod
// thermistor does NOT trigger this: its field just prints nan. The hardware
// thermal switch in series with the TEC is the independent final protection.
//
// To verify: temporarily set this to 30.0, upload, warm the TEC thermistor
// above 30 C, and confirm "safety" reads SHUTDOWN with PWM 0. Then set it back
// to 60.0 and upload again.
const float TEMP_LIMIT_C = 60.0;

// ------------------------------------------------------------------
// COMMAND TIMEOUT (unchanged from Module 5)
// ------------------------------------------------------------------
// The Python GUI sends a SET PWM command after every DATA record (about once per
// second). If no SET PWM command arrives for COMMAND_TIMEOUT_MS while PWM is
// nonzero (Python crashed, GUI frozen, USB unplugged), both H-bridge PWM outputs
// are set to zero. A new command is needed to drive the TEC again.
const unsigned long COMMAND_TIMEOUT_MS = 3000;

// ------------------------------------------------------------------
// EXPERIMENTALLY VERIFIED HEAT/COOL MAPPING (unchanged since Module 4)
// ------------------------------------------------------------------
// HEAT_ACTIVE_PIN = the Arduino pin that must output PWM when HEATING.
// COOL_ACTIVE_PIN = the Arduino pin that must output PWM when COOLING.
// Module 4: confirmed in the TEC start-up test (red trace while heating,
// blue while cooling).
const int HEAT_ACTIVE_PIN = 9;
const int COOL_ACTIVE_PIN = 10;

// ------------------------------------------------------------------
// STATE
// ------------------------------------------------------------------
int currentPwm = 0;          // 0-255, starts at 0
bool currentIsHeat = true;   // true = HEAT, false = COOL, starts as HEAT
bool safetyShutdown = false; // true while the temperature limit holds PWM at 0

float temperaturesC[NUM_CHANNELS];  // most recent averaged temperatures
float setpointC = NAN;              // last SETPOINT command, for the record only

unsigned long startTime;
unsigned long lastCommandMs = 0;    // millis() of the last SET PWM command line

// Running sums for the ADC_SAMPLES average of each channel.
unsigned long adcSum[NUM_CHANNELS];
int adcCount = 0;
unsigned long lastSampleUs = 0;

// Serial line buffer for incoming commands.
String commandBuffer = "";

// ------------------------------------------------------------------
// THERMISTOR MEASUREMENT
// ------------------------------------------------------------------
// Convert an averaged ADC value to temperature (Beta equation), using the
// divider resistor of that channel.
float adcToTemperatureC(float adc, float seriesResistor) {
  if (adc <= 0 || adc >= ADC_MAX) {
    return NAN;
  }

  float resistance = seriesResistor * adc / (ADC_MAX - adc);

  float steinhart = resistance / NOMINAL_RESISTANCE;
  steinhart = log(steinhart);
  steinhart /= BETA_COEFFICIENT;
  steinhart += 1.0 / (NOMINAL_TEMPERATURE_C + 273.15);
  steinhart = 1.0 / steinhart;
  steinhart -= 273.15;

  return steinhart;
}

// Each time SAMPLE_INTERVAL_US has passed, read all six channels once. After
// ADC_SAMPLES readings, update temperaturesC from the averages and return true.
// Spreading the readings across loop() keeps serial commands responsive while
// the averages build up.
bool takeSample() {
  unsigned long nowUs = micros();
  if (nowUs - lastSampleUs < SAMPLE_INTERVAL_US) {
    return false;
  }
  lastSampleUs = nowUs;

  for (int ch = 0; ch < NUM_CHANNELS; ch++) {
    analogRead(THERMISTOR_PINS[ch]);               // settling reading, discarded
    adcSum[ch] += analogRead(THERMISTOR_PINS[ch]);  // kept
  }
  adcCount++;

  if (adcCount < ADC_SAMPLES) {
    return false;
  }

  for (int ch = 0; ch < NUM_CHANNELS; ch++) {
    temperaturesC[ch] = adcToTemperatureC(adcSum[ch] / (float)ADC_SAMPLES,
                                          SERIES_RESISTOR_OHM[ch]);
    adcSum[ch] = 0;
  }
  adcCount = 0;
  return true;
}

// ------------------------------------------------------------------
// SAFETY: apply PWM to the H-bridge
// ------------------------------------------------------------------
// Only one H-bridge input gets PWM at a time. The other is held LOW.
// This prevents both inputs being active at once.
void applyOutput() {
  // Software temperature limit: never drive the TEC during a safety shutdown.
  if (safetyShutdown) {
    zeroOutput();
    return;
  }

  int pwmPin;
  int lowPin;

  if (currentIsHeat) {
    pwmPin = HEAT_ACTIVE_PIN;
    lowPin = COOL_ACTIVE_PIN;
  } else {
    pwmPin = COOL_ACTIVE_PIN;
    lowPin = HEAT_ACTIVE_PIN;
  }

  // Make sure both pins are digital outputs.
  pinMode(HBRIDGE_PIN_1, OUTPUT);
  pinMode(HBRIDGE_PIN_2, OUTPUT);

  // Hold the inactive pin LOW, then write PWM on the active pin.
  digitalWrite(lowPin, LOW);
  analogWrite(pwmPin, currentPwm);
}

// ------------------------------------------------------------------
// SAFETY: zero the output
// ------------------------------------------------------------------
void zeroOutput() {
  currentPwm = 0;
  digitalWrite(HBRIDGE_PIN_1, LOW);
  digitalWrite(HBRIDGE_PIN_2, LOW);
  analogWrite(HBRIDGE_PIN_1, 0);
  analogWrite(HBRIDGE_PIN_2, 0);
}

// ------------------------------------------------------------------
// SAFETY: software temperature limit (TEC channel only)
// ------------------------------------------------------------------
// Called every loop with the most recent averaged TEC temperature.
// Above TEMP_LIMIT_C (or with no valid TEC reading), both H-bridge PWM outputs
// are set to zero. zeroOutput() also clears the commanded PWM, so the TEC does
// not restart by itself when the temperature falls again: a new command from the
// GUI is required.
void checkTemperatureLimit() {
  float tecC = temperaturesC[TEC_CHANNEL];
  bool overLimit = isnan(tecC) || tecC > TEMP_LIMIT_C;

  if (overLimit) {
    zeroOutput();

    if (!safetyShutdown) {
      safetyShutdown = true;
      Serial.print("SAFETY SHUTDOWN ACTIVE: ");
      if (isnan(tecC)) {
        Serial.print("no valid TEC temperature reading (check the A0 thermistor wiring)");
      } else {
        Serial.print("TEC temperature ");
        Serial.print(tecC, 2);
        Serial.print(" C is above the ");
        Serial.print(TEMP_LIMIT_C, 2);
        Serial.print(" C limit");
      }
      Serial.println(". Both H-bridge PWM outputs set to 0.");
    }
  } else if (safetyShutdown) {
    safetyShutdown = false;
    Serial.print("SAFETY SHUTDOWN CLEARED: TEC temperature ");
    Serial.print(tecC, 2);
    Serial.print(" C is back at or below the ");
    Serial.print(TEMP_LIMIT_C, 2);
    Serial.println(" C limit. PWM stays 0 until a new command is sent.");
  }
}

// ------------------------------------------------------------------
// PARSER: SETPOINT command (record only)
// ------------------------------------------------------------------
// Accepted: SETPOINT <number>  or  SETPOINT OFF. The value is only stored for
// the setpoint_C field. A malformed SETPOINT line is ignored with a message; it
// does not change the PWM.
void handleSetpointCommand(String value) {
  value.trim();
  if (value == "OFF") {
    setpointC = NAN;
    return;
  }

  // The value must look like a number: digits, at most one '.', optional '-'.
  bool valid = value.length() > 0;
  int dots = 0;
  for (unsigned int i = 0; i < value.length() && valid; i++) {
    char c = value.charAt(i);
    if (c == '.') {
      dots++;
    } else if (!(isDigit(c) || (c == '-' && i == 0))) {
      valid = false;
    }
  }
  if (!valid || dots > 1) {
    Serial.println("ERROR: malformed SETPOINT command ignored");
    return;
  }
  setpointC = value.toFloat();
}

// ------------------------------------------------------------------
// PARSER: handle one command line
// ------------------------------------------------------------------
// Accepted format (case-insensitive on keywords):
//   SET PWM <0-255> DIR HEAT
//   SET PWM <0-255> DIR COOL
//   SETPOINT <value> | SETPOINT OFF
//
// Any other malformed or unknown command returns PWM to 0.
void handleCommand(String line) {
  line.trim();
  line.toUpperCase();

  // Reject empty lines silently.
  if (line.length() == 0) {
    return;
  }

  // SETPOINT is for the record only: it does not count as a PWM command, so it
  // does not keep the TEC running if Python stops sending SET PWM.
  if (line.startsWith("SETPOINT ")) {
    handleSetpointCommand(line.substring(9));
    return;
  }

  lastCommandMs = millis();

  // Tokenize by spaces.
  // Expected tokens:
  //   0: SET
  //   1: PWM
  //   2: <number>
  //   3: DIR
  //   4: HEAT | COOL
  int t0 = line.indexOf(' ');
  if (t0 < 0) { zeroOutput(); return; }
  String tok0 = line.substring(0, t0);

  int t1 = line.indexOf(' ', t0 + 1);
  if (t1 < 0) { zeroOutput(); return; }
  String tok1 = line.substring(t0 + 1, t1);

  int t2 = line.indexOf(' ', t1 + 1);
  if (t2 < 0) { zeroOutput(); return; }
  String tok2 = line.substring(t1 + 1, t2);

  int t3 = line.indexOf(' ', t2 + 1);
  if (t3 < 0) { zeroOutput(); return; }
  String tok3 = line.substring(t2 + 1, t3);

  String tok4 = line.substring(t3 + 1);
  tok4.trim();

  // Validate keywords.
  if (tok0 != "SET") { zeroOutput(); return; }
  if (tok1 != "PWM") { zeroOutput(); return; }
  if (tok3 != "DIR") { zeroOutput(); return; }
  if (tok4 != "HEAT" && tok4 != "COOL") { zeroOutput(); return; }

  // Validate and parse PWM value.
  // The string must be all digits, else malformed.
  if (tok2.length() == 0) { zeroOutput(); return; }
  for (unsigned int i = 0; i < tok2.length(); i++) {
    if (!isDigit(tok2.charAt(i))) {
      zeroOutput();
      return;
    }
  }

  long pwmValue = tok2.toInt();

  // Clamp numeric PWM to 0-255.
  if (pwmValue < 0) pwmValue = 0;
  if (pwmValue > 255) pwmValue = 255;

  // Commit the new state.
  currentPwm = (int)pwmValue;
  currentIsHeat = (tok4 == "HEAT");

  applyOutput();
}

// ------------------------------------------------------------------
// OUTPUT: one DATA record
// ------------------------------------------------------------------
// Print a float with 2 decimals, or nan for a missing reading.
void printValue(float value) {
  if (isnan(value)) {
    Serial.print("nan");
  } else {
    Serial.print(value, 2);
  }
}

void printDataRecord() {
  float elapsed = (millis() - startTime) / 1000.0;

  Serial.print("DATA,");
  Serial.print(elapsed, 2);                  // time_s
  for (int ch = 0; ch < NUM_CHANNELS; ch++) {
    Serial.print(",");
    printValue(temperaturesC[ch]);           // tec_C, rod1_C ... rod5_C
  }
  Serial.print(",");
  Serial.print(currentPwm);                  // pwm
  Serial.print(",");
  Serial.print(currentIsHeat ? 1 : 0);       // heat_cool
  Serial.print(",");
  printValue(setpointC);                     // setpoint_C
  Serial.print(",");
  Serial.println(safetyShutdown ? "SHUTDOWN" : "OK");  // safety
}

// ------------------------------------------------------------------
// SETUP
// ------------------------------------------------------------------
void setup() {
  pinMode(HBRIDGE_PIN_1, OUTPUT);
  pinMode(HBRIDGE_PIN_2, OUTPUT);

  // Safety: PWM starts at zero.
  zeroOutput();

  Serial.begin(9600);

  startTime = millis();
  commandBuffer.reserve(64);
  for (int ch = 0; ch < NUM_CHANNELS; ch++) {
    adcSum[ch] = 0;
    temperaturesC[ch] = NAN;
  }

  Serial.println("Module 7 six-thermistor rod acquisition (P/PI control runs in Python)");
  Serial.println("Commands: SET PWM <0-255> DIR HEAT | COOL;  SETPOINT <C> | OFF");
  Serial.print("SAFETY: software temperature limit on the TEC thermistor (C): ");
  Serial.println(TEMP_LIMIT_C, 2);
  Serial.print("SAFETY: command timeout (s): ");
  Serial.println(COMMAND_TIMEOUT_MS / 1000.0, 1);

  // Header, printed once. Every later DATA line is one measurement record.
  Serial.println("DATA,time_s,tec_C,rod1_C,rod2_C,rod3_C,rod4_C,rod5_C,pwm,heat_cool,setpoint_C,safety");

  // Build the first average before accepting commands, so the safety check
  // always has a measured TEC temperature to test.
  while (!takeSample()) {
  }
  checkTemperatureLimit();
}

// ------------------------------------------------------------------
// LOOP
// ------------------------------------------------------------------
void loop() {
  // ---- read incoming serial commands ----
  // We read one character at a time, accumulate into commandBuffer,
  // and process on newline.
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '\n' || c == '\r') {
      if (commandBuffer.length() > 0) {
        handleCommand(commandBuffer);
        commandBuffer = "";
      }
    } else {
      if (commandBuffer.length() < 64) {
        commandBuffer += c;
      } else {
        // Line too long: drop it and zero output.
        commandBuffer = "";
        zeroOutput();
      }
    }
  }

  // ---- take one reading of all channels (true when new averages are ready) ----
  bool newTemperatures = takeSample();

  // ---- safety: check the averaged TEC temperature every loop ----
  checkTemperatureLimit();

  // ---- safety: stop the TEC if Python stops sending commands ----
  if (currentPwm > 0 && millis() - lastCommandMs > COMMAND_TIMEOUT_MS) {
    zeroOutput();
    Serial.print("SAFETY: no command for ");
    Serial.print(COMMAND_TIMEOUT_MS / 1000.0, 1);
    Serial.println(" s. Both H-bridge PWM outputs set to 0.");
  }

  // ---- print one DATA record per set of averages (about 1 s) ----
  if (newTemperatures) {
    printDataRecord();
  }
}
