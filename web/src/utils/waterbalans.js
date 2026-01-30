/**
 * Waterbalans berekening utility voor regenbui simulatie
 * 
 * Berekent waterstand veranderingen op basis van:
 * - Regenintensiteit
 * - Gemaal debiet (afvoer)
 * - Verdamping
 * - Infiltratie
 */

/**
 * Bereken waterbalans voor één tijdstap (1 minuut)
 * 
 * @param {Object} params - Berekening parameters
 * @param {number} params.regenIntensiteit - Regenintensiteit in mm/uur
 * @param {number} params.oppervlakte - Oppervlakte peilgebied in m²
 * @param {number} params.gemaalDebiet - Gemaal debiet in m³/s
 * @param {number} params.verdamping - Verdamping in mm/uur
 * @param {number} params.infiltratie - Infiltratie in mm/uur
 * @param {number} params.huidigeWaterstand - Huidige waterstand in m NAP
 * 
 * @returns {Object} - Waterbalans resultaat
 * @returns {number} returns.waterToevoer - Water toevoer in m³/s
 * @returns {number} returns.waterAfvoer - Water afvoer in m³/s
 * @returns {number} returns.waterVerlies - Water verlies in m³/s
 * @returns {number} returns.waterBalans - Netto waterbalans in m³/s
 * @returns {number} returns.waterstandVerandering - Waterstand verandering in m/minuut
 * @returns {number} returns.nieuweWaterstand - Nieuwe waterstand in m NAP
 */
export function calculateWaterBalance(params) {
  const {
    regenIntensiteit, // mm/uur
    oppervlakte, // m²
    gemaalDebiet = 0, // m³/s
    verdamping = 0, // mm/uur
    infiltratie = 0, // mm/uur
    huidigeWaterstand // m NAP
  } = params

  // Converteer mm/uur naar m³/s
  // 1 mm/uur = 1 liter/m²/uur = 0.001 m³/m²/uur
  // Voor oppervlakte: mm/uur * oppervlakte(m²) / 3600 = m³/s
  const mmPerUurToM3PerSec = (mmPerUur, oppervlakteM2) => {
    return (mmPerUur / 1000) * oppervlakteM2 / 3600
  }

  // Water toevoer (regen)
  const waterToevoer = mmPerUurToM3PerSec(regenIntensiteit, oppervlakte)

  // Water afvoer (gemaal)
  const waterAfvoer = gemaalDebiet

  // Water verlies (verdamping + infiltratie)
  const waterVerlies = mmPerUurToM3PerSec(verdamping + infiltratie, oppervlakte)

  // Netto waterbalans
  const waterBalans = waterToevoer - waterAfvoer - waterVerlies

  // Waterstand verandering (m per minuut)
  // dV/dt = waterBalans [m³/s]
  // dh/dt = dV/dt / oppervlakte [m/s]
  // dh/dt per minuut = dh/dt * 60 [m/minuut]
  const waterstandVerandering = (waterBalans / oppervlakte) * 60

  // Nieuwe waterstand
  const nieuweWaterstand = huidigeWaterstand + waterstandVerandering

  return {
    waterToevoer,
    waterAfvoer,
    waterVerlies,
    waterBalans,
    waterstandVerandering,
    nieuweWaterstand
  }
}

/**
 * Bereken tijdreeks van waterstand over simulatie periode
 * 
 * @param {Object} params - Simulatie parameters
 * @param {number} params.startWaterstand - Start waterstand in m NAP
 * @param {number} params.regenIntensiteit - Regenintensiteit in mm/uur
 * @param {number} params.regenDuur - Regen duur in minuten
 * @param {number} params.oppervlakte - Oppervlakte peilgebied in m²
 * @param {number} params.gemaalDebiet - Gemaal debiet in m³/s
 * @param {number} params.verdamping - Verdamping in mm/uur
 * @param {number} params.infiltratie - Infiltratie in mm/uur
 * @param {number} params.naRegenDuur - Duur na regenbui in minuten (default 30)
 * @param {number} params.tijdStap - Tijdstap in minuten (default 1)
 * 
 * @returns {Array} - Array van tijdstappen met waterstand data
 */
export function calculateTimeSeries(params) {
  const {
    startWaterstand,
    regenIntensiteit,
    regenDuur,
    oppervlakte,
    gemaalDebiet = 0, // Dit is nu de capaciteit als smartControl=true
    verdamping = 0,
    infiltratie = 0,
    naRegenDuur = 30,
    tijdStap = 1,
    smartControl = false, // Nieuwe parameter
    streefpeil = 0, // Nodig voor smartControl
    marge = 0 // Nodig voor smartControl (cm)
  } = params

  const tijdstappen = []
  let huidigeWaterstand = startWaterstand
  let tijd = 0

  // Totale simulatie duur
  const totaleDuur = regenDuur + naRegenDuur

  // Converteer marge naar meters
  const margeMeters = marge / 100
  // Bovenkant marge = inschakelpeil
  const inschakelPeil = streefpeil + margeMeters
  // Streefpeil = uitschakelpeil (of iets daaronder? Laten we streefpeil aanhouden)
  const uitschakelPeil = streefpeil

  let pompStatus = false // false = uit, true = aan

  // PID Controller statics
  let integral = 0
  let lastError = 0

  // PID Constants (getuned voor waterbeheer)
  // Kp: 0.20m fout geeft 100% actie -> Kp = 5
  // Ki: Langzame opbouw om steady-state error weg te werken
  // Kd: Demping op snelle veranderingen
  const Kp = 5.0
  const Ki = 0.05
  const Kd = 20.0

  while (tijd <= totaleDuur) {
    // Bepaal of het regent
    const isRegen = tijd <= regenDuur
    const actueleRegenIntensiteit = isRegen ? regenIntensiteit : 0

    // Bepaal actueel gemaal debiet
    let actueelDebiet = gemaalDebiet

    if (smartControl) {
      // PID Control Logic
      const error = huidigeWaterstand - streefpeil
      const dt = tijdStap // minuten

      // Alleen integreren als we niet op max zitten (anti-windup)
      // en als we daadwerkelijk moeten pompen (water > streefpeil)
      if (Math.abs(error) > 0.001) {
        integral += error * dt
      }

      const derivative = (error - lastError) / dt

      // PID Formule: u(t) = Kp*e + Ki*∫e + Kd*de/dt
      let output = (Kp * error) + (Ki * integral) + (Kd * derivative)

      // Clamp output tussen 0 en 1 (0% en 100%)
      if (output < 0) output = 0
      if (output > 1) output = 1

      // Anti-windup clamping
      if ((output === 0 && error < 0) || (output === 1 && error > 0)) {
        // Stop integratie als we tegen limiet aanlopen
        integral -= error * dt
      }

      actueelDebiet = gemaalDebiet * output
      pompStatus = actueelDebiet > 0.001

      lastError = error
    }

    // Bereken waterbalans voor deze tijdstap
    const balans = calculateWaterBalance({
      regenIntensiteit: actueleRegenIntensiteit,
      oppervlakte,
      gemaalDebiet: actueelDebiet,
      verdamping,
      infiltratie,
      huidigeWaterstand
    })

    // Sla tijdstap op
    tijdstappen.push({
      tijd: tijd, // minuten
      waterstand: huidigeWaterstand,
      waterToevoer: balans.waterToevoer,
      waterAfvoer: balans.waterAfvoer,
      waterVerlies: balans.waterVerlies,
      waterBalans: balans.waterBalans,
      isRegen: isRegen,
      isPompAan: pompStatus // Voor visualisatie
    })

    // Update waterstand voor volgende tijdstap
    huidigeWaterstand = balans.nieuweWaterstand
    tijd += tijdStap
  }

  return tijdstappen
}

/**
 * Bereken drooglegging en overschrijding
 * 
 * @param {Object} params - Parameters
 * @param {number} params.maaiveldNiveau - Maaiveld niveau in m NAP
 * @param {number} params.waterstand - Waterstand in m NAP
 * @param {number} params.streefpeil - Streefpeil in m NAP
 * @param {number} params.marge - Drooglegging marge in cm
 * 
 * @returns {Object} - Drooglegging resultaat
 */
export function calculateDrooglegging(params) {
  const {
    maaiveldNiveau,
    waterstand,
    streefpeil,
    marge // cm
  } = params

  // Drooglegging = maaiveld - waterstand
  const drooglegging = maaiveldNiveau - waterstand

  // Streef drooglegging = maaiveld - streefpeil
  const streefDrooglegging = maaiveldNiveau - streefpeil

  // Minimale toegestane drooglegging = streef drooglegging - marge
  const minimaleDrooglegging = streefDrooglegging - (marge / 100) // Converteer cm naar m

  // Overschrijding (negatief = binnen marge, positief = buiten marge)
  const overschrijding = minimaleDrooglegging - drooglegging

  return {
    drooglegging, // m
    streefDrooglegging, // m
    minimaleDrooglegging, // m
    overschrijding, // m (positief = te weinig drooglegging)
    overschrijdingCm: overschrijding * 100 // cm
  }
}

/**
 * Vind minimaal benodigd debiet om drooglegging binnen marge te houden
 * 
 * @param {Object} params - Simulatie parameters
 * @param {number} params.startWaterstand - Start waterstand in m NAP
 * @param {number} params.regenIntensiteit - Regenintensiteit in mm/uur
 * @param {number} params.regenDuur - Regen duur in minuten
 * @param {number} params.oppervlakte - Oppervlakte peilgebied in m²
 * @param {number} params.maaiveldNiveau - Maaiveld niveau in m NAP
 * @param {number} params.streefpeil - Streefpeil in m NAP
 * @param {number} params.marge - Drooglegging marge in cm
 * @param {number} params.verdamping - Verdamping in mm/uur
 * @param {number} params.infiltratie - Infiltratie in mm/uur
 * @param {number} params.stapGrootte - Stapgrootte voor iteratie in m³/s (default 0.1)
 * @param {number} params.maxDebiet - Maximum debiet voor iteratie in m³/s (default 100)
 * 
 * @returns {Object} - Resultaat met minimaal debiet
 */
export function findMinimumDebiet(params) {
  const {
    startWaterstand,
    regenIntensiteit,
    regenDuur,
    oppervlakte,
    maaiveldNiveau,
    streefpeil,
    marge,
    verdamping = 0,
    infiltratie = 0,
    stapGrootte = 0.1,
    maxDebiet = 100
  } = params

  // Start met een snelle schatting gebaseerd op regenintensiteit
  // Regen toevoer = regenIntensiteit (mm/uur) * oppervlakte (m²) / 3600 = m³/s
  const geschatDebiet = (regenIntensiteit / 1000) * oppervlakte / 3600 // m³/s
  let debiet = Math.max(0, geschatDebiet * 0.8) // Start iets lager dan geschat voor veiligheid
  let maxOverschrijding = 0
  let tijdstappenMetOverschrijding = []

  // Itereer tot we een debiet vinden dat binnen marge blijft
  while (debiet <= maxDebiet) {
    // Bereken tijdreeks met dit debiet
    const tijdstappen = calculateTimeSeries({
      startWaterstand,
      regenIntensiteit,
      regenDuur,
      oppervlakte,
      gemaalDebiet: debiet,
      verdamping,
      infiltratie
    })

    // Check alle tijdstappen voor overschrijding
    let maxOverschrijdingVoorDebiet = 0
    const overschrijdingen = []

    for (const stap of tijdstappen) {
      const drooglegging = calculateDrooglegging({
        maaiveldNiveau,
        waterstand: stap.waterstand,
        streefpeil,
        marge
      })

      if (drooglegging.overschrijding > 0) {
        maxOverschrijdingVoorDebiet = Math.max(
          maxOverschrijdingVoorDebiet,
          drooglegging.overschrijding
        )
        overschrijdingen.push({
          tijd: stap.tijd,
          waterstand: stap.waterstand,
          overschrijding: drooglegging.overschrijdingCm
        })
      }
    }

    // Als geen overschrijdingen, hebben we het minimale debiet gevonden
    if (maxOverschrijdingVoorDebiet === 0) {
      return {
        minimaalDebiet: debiet,
        maxOverschrijding: 0,
        tijdstappenMetOverschrijding: [],
        tijdstappen: tijdstappen,
        success: true
      }
    }

    // Update tracking
    maxOverschrijding = maxOverschrijdingVoorDebiet
    tijdstappenMetOverschrijding = overschrijdingen

    // Verhoog debiet en probeer opnieuw
    debiet += stapGrootte
  }

  // Als we hier komen, hebben we geen debiet gevonden binnen maxDebiet
  return {
    minimaalDebiet: null,
    maxOverschrijding: maxOverschrijding * 100, // Converteer naar cm
    tijdstappenMetOverschrijding,
    success: false,
    message: `Geen debiet gevonden binnen ${maxDebiet} m³/s`
  }
}

/**
 * Bereken maximale waterstand tijdens simulatie
 * 
 * @param {Array} tijdstappen - Tijdstappen array van calculateTimeSeries
 * @returns {Object} - Maximale waterstand data
 */
export function findMaxWaterstand(tijdstappen) {
  if (!tijdstappen || tijdstappen.length === 0) {
    return { maxWaterstand: null, tijd: null }
  }

  let maxWaterstand = tijdstappen[0].waterstand
  let maxTijd = tijdstappen[0].tijd

  for (const stap of tijdstappen) {
    if (stap.waterstand > maxWaterstand) {
      maxWaterstand = stap.waterstand
      maxTijd = stap.tijd
    }
  }

  return {
    maxWaterstand,
    tijd: maxTijd
  }
}

