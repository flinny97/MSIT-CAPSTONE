Assignment Activity Unit 4

Frank Lin
University of the People
MSIT 5910-01 - AY2027-T1
Dr. Stella T. Whyte
September 30, 2026










Introduction
Modern IT projects require teams to build, test, and release systems quickly without compromising quality. As systems become more complex, manual integration and deployment can create delays, errors, and inconsistencies. Continuous Integration and Continuous Deployment, known as CI/CD, help address these challenges by automating many of the steps involved in moving changes from development into a working environment. Instead of waiting until the end of a project to combine everyone’s work, teams can integrate smaller updates throughout the development cycle and identify problems earlier. This report explains what CI/CD is, the tools used to support it, the benefits it provides, and how I could apply these practices to my own project.
Definition and Relevance of CI/CD
Continuous Integration is a practice where team members frequently merge their changes into a shared repository so updates can be tested and combined automatically (Red Hat, 2025). Continuous Deployment extends this by automatically releasing changes into a production environment once required tests have been passed. The purpose of both is to reduce the manual work involved in combining, testing, and releasing changes. Narasimhan et al. (2025) describe continuous integration, continuous delivery, monitoring, and feedback as the core stages of the DevOps lifecycle. In traditional development, developers work separately for long periods before combining their work. This creates conflicts that are hard to trace back and review. CI reduces that risk because the updates are smaller and more frequent. CD then turns releasing those updates into a repeatable process rather than a manual event. DevOps depends on automation, collaboration, and continuous feedback so that development and operations teams can deliver more quickly and reliably. According to Oguz (2025), Agile development focuses on making progress through smaller and more frequent improvements. CI/CD supports this approach by allowing teams to release updates throughout the project instead of depending on one large release at the end. This is relevant in modern software engineering because organizations need to update systems regularly while still keeping them stable and reliable.

CI/CD Tools and Technologies
Several tools are used to build and run CI/CD pipelines such as GitHub Actions, Jenkins, GitLab CI/CD, and Azure DevOps. GitHub Actions is built directly into GitHub and can run automated workflows when an event happens in a repository (GitHub, n.d.). For example, a workflow can run a full set of tests every time someone pushes a commit and block the merge if a test fails. Jenkins is an automation server that runs on hardware the organization controls. This provides more control over the build environment, but it also means an individual has to maintain the server. GitLab CI/CD keeps the pipeline definition in a file inside the repository itself, so the build process is version controlled along with the code.
Azure DevOps provides pipelines, repositories, testing tools, and project tracking. It is common in organizations that already use Microsoft products because it connects to existing accounts and licensing (Microsoft, n.d.). These tools differ in design, but they serve the same general purpose of automating repeatable work that would need to be completed manually. Automation and continuous integration are important DevOps practices because they improve consistency and reduce repetitive work for development and operations teams (Parzych, 2019). The right tool depends on factors such as cost, current technology, project size, and the experience of the team. A smaller project may only need GitHub Actions. A larger organization may need a more flexible platform such as Jenkins or Azure DevOps.
Collaboration, Integration, and Faster Delivery
CI/CD improves collaboration because developers and operations staff work from one shared process. Instead of treating development and deployment as separate jobs, teams work better together when tools are unified. When developers submit smaller updates, other team members review them earlier and can catch conflicts before they grow. Automated testing gives quick feedback when a change breaks something. The problem is fixed while the work is still recent. This reduces integration issues because the team is not merging large amounts of separate work at the end of a development cycle. When teams move away from separate processes and work together through a shared workflow, CI/CD provides the automation needed to make this approach more effective (Red Hat, 2025). Another major benefit of CI/CD is faster delivery. When building, testing, and deployment are automated, work moves through those stages quicker and with fewer manual mistakes. I see this frequently in my career in IT. For example, a system release that depends on one person remembering every manual step can easily fail if even one step is missed. This does not mean every update should be released without review. Approval requirements, security checks, and testing standards can still be included within the pipeline to maintain control and reliability.
Applying CI/CD to My Capstone Project
CI/CD practices can be applied to my Improving Employee Phishing Awareness and Response project even though it is much smaller than a fully developed system. The project is already tracked in a Git repository with two permanent branches. All working commits go on the development branch. The main branch only receives changes through a reviewed merge at a unit milestone. The scoring code that calculates the evaluation metrics is currently covered by twelve automated tests. At the moment, I run those tests myself. This means that the check only works if I remember to run them. A GitHub Actions workflow could close this gap by automatically running all twelve tests whenever a change is pushed to the development branch and preventing the merge into main if any test fails. My scoring code is also designed to reject any assessment file that contains a participant name or email address. An automated check could enforce this privacy rule with every change instead of depending on me to verify it manually. Prototyping is useful because an early working version allows design decisions to be tested against actual results instead of assumptions alone (Laptick, 2022). Using CI/CD in this manner would make the project more reliable, reduce the chance of human error, and make it easier to expand the project later.








References
GitHub. (n.d.). GitHub Actions. https://github.com/features/actions
Laptick, S. (2022, November 9). How SDLC prototype model helps build comprehensive apps when requirements are unclear. XB Software. https://xbsoftware.com/blog/prototype-model-sdlc/
Microsoft. (n.d.). Azure DevOps. https://azure.microsoft.com/en-us/products/devops
Narasimhan, A., Sham, R., & Subramanian, H. (2025, October 15). A beginner's handbook to DevOps [White paper]. Dell Technologies. https://awsprod.merlot.org/merlot/viewMaterial.htm?id=773474552
Oguz, A. (2025). Project management (2nd ed.). MSL Academic Endeavors. https://pressbooks.ulib.csuohio.edu/projectmanagement2ndedition/
Parzych, D. (2019, December 30). 8 must-read DevOps articles for success in 2020. Opensource.com. https://opensource.com/article/19/12/devops-resources
Red Hat. (2025, June 10). What is CI/CD? https://www.redhat.com/en/topics/devops/what-is-ci-cd


