# Blockchain-Based-MedRec-with-BioAuth
The volume of electronic medical records has rapidly burgeoned in recent times. This poses a problem with security and availability as these data need to be accessed from within a hospital as well as, from the outside by the researchers and other hospitals. This means the data should be highly available at all times also taking into consideration emergency situations where medical data is needed immediately to provide further treatment. 

To address the high availability, data integrity and security concerns in the situations aforementioned, we propose the use of Blockchain-based(Ethereum-based) implementation of a Medical Records System with an augmented access delegation protocol. This access delegation protocol is based on ‘OAuth’ authorization along with biometrics to facilitate the quick transfer of data from the host hospital to third party sites. Hence, this protocol will ensure
interoperability of data for patients who want to migrate to another hospital.

It is not necessary that the data should be stored in the blockchain itself. Rather, the data can be maintained off-the-chain on the Cloud. In the footsteps of this notion, we want to ensure that the data is sanitized before being sent to the cloud.
So, we heartily implement the idea suggested by Victoria Fehr & Marc Fischlin in their research to use sanitization over encrypted data rather than on the original data, that is, double encryption of the original data.

The proposed system thus developed, when deployed in a Production
environment as a Distributed Application (DApp) would be impossible to penetrate
and have zero downtime.
